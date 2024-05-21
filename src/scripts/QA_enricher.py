from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
from datasets import load_dataset
import torch
import re

model_id = "google/gemma-1.1-2b-it"
dtype = torch.bfloat16

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cuda",
    torch_dtype=dtype,
)

dataset = load_dataset('squad')


# Function to paraphrase a questions
def paraphrase_question(question, model, amount, max_new_tokens):
  chat = [
    { "role": "user", "content": f"Rephrase the following question {amount} times: '{question}'" },
  ]
  prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
  inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
  outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=max_new_tokens, do_sample=True)
  paraphrased_questions = tokenizer.decode(outputs[0])
  return paraphrased_questions


# Function to paraphrase a batch of questions
def paraphrase_questions(questions, model, tokenizer):
    paraphrased_questions = []
    for question in questions:
        paraphrased_question = paraphrase_question(question, model, "10", 150)
        paraphrased_questions.append(re.search(r'(?<=<start_of_turn>model)(.*)', paraphrased_question, re.DOTALL).group(1))
    return paraphrased_questions

# Function to paraphrase a questions
def paraphrase_answer(answer, model, amount, max_new_tokens):
  chat = [
    { "role": "user", "content": f"Rephrase the following answer {amount} times: '{answer}'" },
  ]
  prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
  inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
  outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=max_new_tokens, do_sample=True)
  paraphrased_answers = tokenizer.decode(outputs[0])
  return paraphrased_answers


# Function to paraphrase a batch of questions
def paraphrase_answers(answers, model, tokenizer):
    paraphrased_answers = []
    for answer in answers:
        paraphrased_answer = paraphrase_answer(answer['text'][0], model, "5", 150)
        paraphrased_answers.append(re.search(r'(?<=<start_of_turn>model)(.*)', paraphrased_answer, re.DOTALL).group(1))
    return paraphrased_answers

# Extract questions from the dataset  
questions = [item for item in dataset['train'][:2]['question']] # Adjust the range as needed
# Paraphrase the questions
paraphrased_questions = paraphrase_questions(questions, model, tokenizer)

# Print some examples
for original, paraphrased in zip(questions[:5], paraphrased_questions[:5]):
    print(f"Original: {original}")
    print(f"Paraphrased: {paraphrased}")
    print()
  
# Extract answers from the dataset  
answers = [item for item in dataset['train'][:2]['answers']] # Adjust the range as needed
# Paraphrase the questions
paraphrased_answers = paraphrase_answers(answers, model, tokenizer)

# Print some examples
for original, paraphrased in zip(answers[:5], paraphrased_answers[:5]):
    print(f"Original: {original['text'][0]}")
    print(f"Paraphrased: {paraphrased}")
    print()
