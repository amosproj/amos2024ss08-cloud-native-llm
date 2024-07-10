from huggingface_hub import HfApi, login
import os
HF_TOKEN = os.getenv('HF_TOKEN', 'add_token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)

from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
from datasets import load_dataset
import torch
import re
from tqdm import tqdm

import csv

model_id = "google/gemma-1.1-7b-it"
dtype = torch.bfloat16
torch.cuda.empty_cache()

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cuda",
    torch_dtype=dtype,
)

dataset = load_dataset("Kubermatic/cncf-raw-data-for-llm-training", split="train")

#taken in parts from https://medium.com/@lucamassaron/sherlock-holmes-q-a-enhanced-with-gemma-2b-it-fine-tuning-2907b06d2645

def gemma_result(question, model=model, tokenizer=tokenizer, temperature=0.0, max_new_tokens = 256, return_answer=False):
    input_ids = tokenizer(question, return_tensors="pt").to("cuda")
    if temperature > 0:
        do_sample=True
        outputs = model.generate(**input_ids,
                                max_new_tokens=max_new_tokens,
                                do_sample=do_sample,
                                temperature=temperature)
    else:
        do_sample=False
        outputs = model.generate(**input_ids,
                                max_new_tokens=max_new_tokens)
    result = str(tokenizer.decode(outputs[0])).replace("<bos>", "").replace("<eos>", "").strip()
    if return_answer:
        return result
    else:
        print(result)

qa_data = []
fail_count = 0


def extract_json(text, word):
    pattern = fr'"{word}": "(.*?)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return ""
# chunks = 2 # increment this number up to len(extracted_texts)

question = ""
answer = ""
question_ratio = 1000 # decrement this number to produce more questions (suggested: 24)

for i in tqdm(range(len(dataset['content'][:20]))):
    text_category = dataset['tag'][i]['category']
    text_subcategory = dataset['tag'][i]['subcategory']
    text_project = dataset['tag'][i]['project_name']
    text_file = dataset['tag'][i]['file_name']
    chunks = dataset['content'][i]

    for chunk in chunks:
        information_chunk = chunk["data"]  
        print(information_chunk)
        question_text = f"""Create a question and its answer from the following piece of information for a project of the Cloud Native Computing Foundation landscape,
            do not assume the reader knows the text hence put all the necessary information into the question,
            and return it exclusively in JSON format in the format {'{"question": "...", "answer": "..."}'}.
            Here is the piece of information to elaborate:
            "{information_chunk}"

            OUTPUT JSON:
            """
        result = gemma_result(question_text, model=model, temperature=0, return_answer=True)
        result = result.split("OUTPUT JSON:")[-1]
        question = extract_json(result, "question")
        answer = extract_json(result, "answer")
        with open('output/qa_results.csv', 'a+', newline='') as file:
            write = csv.writer(file)
            write.writerow([f"{question}",f"{answer}",f"{text_project}", f"{text_file}", f"{text_subcategory}", f"{text_category}"])
# opening the csv file in 'a+' mode

