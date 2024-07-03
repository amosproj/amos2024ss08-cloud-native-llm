from huggingface_hub import HfApi, login
import os
HF_TOKEN = os.getenv('HF_TOKEN', 'Add Token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
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
dataset = load_dataset("Kubermatic/cncf-question-and-answer-dataset-for-llm-training", split="train[:50]")

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
    config = PeftConfig.from_pretrained("Kubermatic/DeepCNCF")
    base_model = AutoModelForCausalLM.from_pretrained("google/gemma-1.1-7b-it")
    model = PeftModel.from_pretrained(base_model, "Kubermatic/DeepCNCF")
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-1.1-7b-it")
    model.eval()

    start_index = int(rank * data_length / world_size) 
    end_index = data_length if rank == NUM_GPUS else int((rank + 1) * data_length / world_size - 1) 

    with torch.no_grad():
        for i in tqdm(range(start_index, end_index)):
            chunks = dataset['Question'][i]

            try:
                result = gemma_result(chunks, model=model, tokenizer=tokenizer, rank=rank, temperature=0, return_answer=True)
                print(result)

                with open(f"output/benchmark_results_cncf_{rank}.csv", 'a+', newline='') as file:
                    write = csv.writer(file)
                    write.writerow([result])

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
    data_length = len(dataset['Question'])
    mp.spawn(run_inference,
             args=(NUM_GPUS, data_length),
             nprocs=NUM_GPUS,
             join=True)
