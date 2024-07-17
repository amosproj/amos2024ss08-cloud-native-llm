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
from peft import PeftModel, PeftConfig


import csv
import gc
import traceback
NUM_GPUS = 1
dataset = load_dataset("Kubermatic/Merged_QAs", split="train[-50:]")

# Function to run inference
def run_inference(rank, world_size, data_length):
    dist.init_process_group("gloo", rank=rank, world_size=world_size)

    config = PeftConfig.from_pretrained("Kubermatic/DeepCNCF9BAdapter")
    base_model = AutoModelForCausalLM.from_pretrained("google/gemma-2-9b-it", device_map=f"cuda:{rank}")
        
    model = PeftModel.from_pretrained(base_model, "Kubermatic/DeepCNCF9BAdapter", device_map=f"cuda:{rank}")
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it")
    model.eval()

    start_index = int(rank * data_length / world_size) 
    end_index = data_length if rank == NUM_GPUS else int((rank + 1) * data_length / world_size - 1) 

    with torch.no_grad():
        for i in tqdm(range(start_index, end_index)):
            question = dataset['Question'][i]

            try:
                chat = [
                    { "role": "user", "content": question},
                ]
                prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
                input_ids = tokenizer(prompt, add_special_tokens=False, return_tensors="pt").to("cuda")

                outputs = model.generate(**inputs,
                                 max_new_tokens=512,
                                 do_sample=True)
                result = tokenizer.decode(outputs[0])
                print(result)

                with open(f"output/benchmark_results{rank}.csv", 'a+', newline='') as file:
                    write = csv.writer(file)
                    write.writerow([result])

                # Clean up to free memory
                del  question_text, result, question, answer
                torch.cuda.empty_cache()
                gc.collect()
            except Exception as error:
                print("An error occurred:", type(error).__name__, "–", error, flush = True)
                torch.cuda.empty_cache()
                gc.collect()

    del model
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
