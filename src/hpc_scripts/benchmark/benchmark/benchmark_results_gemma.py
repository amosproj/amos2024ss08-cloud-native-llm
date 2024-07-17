from huggingface_hub import HfApi, login
import os
HF_TOKEN = os.getenv('HF_TOKEN', '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')
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
NUM_GPUS = 1
dataset = load_dataset("Kubermatic/Merged_QAs", split="train[-50:]")

# Helper function to extract JSON values
def extract_json(text, word):
    pattern = fr'"{word}": "(.*?)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return ""

# Function to generate results using the model
def gemma_result(question, model, tokenizer, rank, temperature=0.0, max_new_tokens=512, return_answer=False):
    chat = [
        { "role": "user", "content": question},
    ]
    prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    input_ids = tokenizer(prompt, add_special_tokens=False, return_tensors="pt").to("cuda")

    
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
    model_id = "google/gemma-2-9b-it"
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

    start_index = int(rank * data_length / world_size) 
    end_index = data_length if rank == NUM_GPUS else int((rank + 1) * data_length / world_size - 1) 

    with torch.no_grad():
        for i in tqdm(range(start_index, end_index)):
            chunks = dataset['Question'][i]

            try:
                result = gemma_result(chunks, model=model, tokenizer=tokenizer, rank=rank, temperature=0, return_answer=True)
                print(result)

                with open(f"output/benchmark_results{rank}.csv", 'a+', newline='') as file:
                    write = csv.writer(file)
                    write.writerow([result])

                # Clean up to free memory
                del result, question
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
    data_length = len(dataset['Question'])
    mp.spawn(run_inference,
             args=(NUM_GPUS, data_length),
             nprocs=NUM_GPUS,
             join=True)
