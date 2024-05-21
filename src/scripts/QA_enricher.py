from transformers import T5Tokenizer, T5ForConditionalGeneration
from datasets import load_dataset
import torch
dataset = load_dataset('squad')


model_name = 'google-t5/t5-small'
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

# Function to paraphrase a batch of questions
def paraphrase_questions(questions, model, tokenizer, batch_size=8):
    paraphrased_questions = []
    for i in range(0, len(questions), batch_size):
        batch = questions[i:i+batch_size]
        inputs = tokenizer(
            [f"paraphrase: {question}" for question in batch], 
            return_tensors="pt", 
            padding=True, 
            truncation=True
        )
        outputs = model.generate(**inputs)
        paraphrased_batch = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        paraphrased_questions.extend(paraphrased_batch)
    return paraphrased_questions

# Extract questions from the dataset  
questions = [item for item in dataset['train'][:10]['question']] # Adjust the range as needed
# Paraphrase the questions
paraphrased_questions = paraphrase_questions(questions, model, tokenizer)

# Print some examples
for original, paraphrased in zip(questions[:5], paraphrased_questions[:5]):
    print(f"Original: {original}")
    print(f"Paraphrased: {paraphrased}")
    print()
