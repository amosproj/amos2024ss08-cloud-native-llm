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

# Function to run inference
def run_inference(rank, world_size, data_length):
    dist.init_process_group("gloo", rank=rank, world_size=world_size)
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()

    start_index = int(rank * data_length / world_size) 
    end_index = data_length if rank == NUM_GPUS else int((rank + 1) * data_length / world_size - 1) 

    with torch.no_grad():
        for i in tqdm(range(start_index, end_index)):
            question = dataset['Question'][i]

            try:
                messages = [
                    {"role": "user", "content": question}
                ]

                input_ids = tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    return_tensors="pt"
                ).to(model.device)

                terminators = [
                    tokenizer.eos_token_id,
                    tokenizer.convert_tokens_to_ids("<|eot_id|>")
                ]

                outputs = model.generate(
                    input_ids,
                    max_new_tokens=512,
                    eos_token_id=terminators,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )
                result = outputs[0][input_ids.shape[-1]:]
                result = tokenizer.decode(result, skip_special_tokens=True)
                print(result)

                with open(f"output/benchmark_results{rank}.csv", 'a+', newline='') as file:
                    write = csv.writer(file)
                    write.writerow([result])

                # Clean up to free memory
                del question_text, result, question, answer
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
