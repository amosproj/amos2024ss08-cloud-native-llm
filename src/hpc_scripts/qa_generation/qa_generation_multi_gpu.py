from huggingface_hub import HfApi, login
import os
HF_TOKEN = os.getenv('HF_TOKEN', 'add_token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import transformers
from datasets import load_dataset
import torch
import re
from tqdm import tqdm
import torch.distributed as dist
import torch.multiprocessing as mp
from multiprocessing import freeze_support

import csv
import gc
import traceback
NUM_GPUS = 4
dataset = load_dataset("Kubermatic/cncf-raw-data-for-llm-training", split="train")

# Helper function to extract JSON values
def extract_json(text, word):
    pattern = fr'"{word}": "(.*?)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return ""

# Function to generate results using the model
def gemma_result(question, model, tokenizer, rank, temperature=0.0, max_new_tokens=256, return_answer=False):
    input_ids = tokenizer(question, return_tensors="pt").to(f"cuda:{rank}")
    
    if temperature > 0:
        do_sample = True
        outputs = model.generate(**input_ids,
                                 max_new_tokens=max_new_tokens,
                                 do_sample=do_sample,
                                 temperature=temperature)
    else:
        do_sample = False
        outputs = model.generate(**input_ids,
                                 max_new_tokens=max_new_tokens)
    result = str(tokenizer.decode(outputs[0])).replace("<bos>", "").replace("<eos>", "").strip()
    del outputs
    del input_ids
    torch.cuda.empty_cache()
    if return_answer:
        return result
    else:
        print(result)

# Function to run inference
def run_inference(rank, world_size, data_length):
    dist.init_process_group("gloo", rank=rank, world_size=world_size)
    model_id = "google/gemma-1.1-7b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    quantization_config = BitsAndBytesConfig(load_in_4bit=True,
                                             bnb_4bit_use_double_quant=True,
                                             bnb_4bit_quant_type="nf4",
                                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quantization_config,
        device_map=f"cuda:{rank}",
    )
    model.eval()

    start_index = int(rank * data_length / world_size) + 8895
    end_index = data_length if rank == NUM_GPUS else int((rank + 1) * data_length / world_size - 1) 

    with torch.no_grad():
        for i in tqdm(range(start_index, end_index)):
            text_category = dataset['tag'][i]['category']
            text_subcategory = dataset['tag'][i]['subcategory']
            text_project = dataset['tag'][i]['project_name']
            text_file = dataset['tag'][i]['file_name']
            chunks = dataset['content'][i]

            for chunk in chunks:
                information_chunk = chunk["data"]
                question_text = f"""Create a question and its answer from the following piece of information for a project of the Cloud Native Computing Foundation landscape,
                do not assume the reader knows the text hence put all the necessary information into the question,
                and return it exclusively in JSON format in the format {'{"question": "...", "answer": "..."}'}.
                Here is the piece of information to elaborate:
                "{information_chunk}"

                OUTPUT JSON:
                """
                try:
                    result = gemma_result(question_text, model=model, tokenizer=tokenizer, rank=rank, temperature=0, return_answer=True)
                    result = result.split("OUTPUT JSON:")[-1]
                    question = extract_json(result, "question")
                    answer = extract_json(result, "answer")

                    with open(f"output/qa_results_{rank}.csv", 'a+', newline='') as file:
                        write = csv.writer(file)
                        write.writerow([question, answer, text_project, text_file, text_subcategory, text_category])

                    # Clean up to free memory
                    del information_chunk, question_text, result, question, answer
                    torch.cuda.empty_cache()
                    gc.collect()
                except Exception as error:
                    print("An error occurred:", type(error).__name__, "–", error, flush = True)
                    torch.cuda.empty_cache()
                    gc.collect()

    del model, tokenizer
    torch.cuda.empty_cache()
    gc.collect()

# Main script
if __name__ == '__main__':
    freeze_support()
    data_length = len(dataset['content'])
    mp.spawn(run_inference,
             args=(NUM_GPUS, data_length),
             nprocs=NUM_GPUS,
             join=True)
