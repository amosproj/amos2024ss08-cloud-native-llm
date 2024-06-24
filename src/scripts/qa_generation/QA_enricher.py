"""
This script demonstrates how to use a causal language model from the Hugging Face Transformers library
to paraphrase questions and answers from the SQuAD dataset.

Libraries Used:
- transformers: For loading the pretrained language model and tokenizer.
- datasets: For loading the SQuAD dataset.
- torch: For tensor computations.
- re: For regular expression operations.

Steps:
1. Load a pretrained language model and tokenizer ('google/gemma-1.1-2b-it') suitable for causal language modeling.
2. Load the SQuAD dataset using the 'datasets' library.
3. Define functions to paraphrase individual questions and answers using the model:
   - `paraphrase_question`: Takes a question, generates multiple paraphrased versions.
   - `paraphrase_questions`: Paraphrases a batch of questions.
   - `paraphrase_answer`: Takes an answer, generates multiple paraphrased versions.
   - `paraphrase_answers`: Paraphrases a batch of answers.
4. Extract questions and answers from the SQuAD dataset.
5. Paraphrase the extracted questions and answers using the defined functions.
6. Print some examples of original and paraphrased questions and answers.

Example usage:
Run the script to load the pretrained model, paraphrase questions and answers from the SQuAD dataset,
and print the results.
"""

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
def paraphrase_question(question: str, model: PreTrainedModel, amount: int, max_new_tokens: int) -> str:
  """
  Paraphrases a given question multiple times using a language model.

  Args:
      question (str): The original question to paraphrase.
      model (PreTrainedModel): The pre-trained language model for generation.
      tokenizer (PreTrainedTokenizer): The tokenizer associated with the model.
      amount (int): The number of paraphrased questions to generate.
      max_new_tokens (int): The maximum number of new tokens to generate.

  Returns:
      str: A string containing the paraphrased questions separated by newlines.
  """

  chat = [
    { "role": "user", "content": f"Rephrase the following question {amount} times: '{question}'" },
  ]
  prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
  inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
  outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=max_new_tokens, do_sample=True)
  paraphrased_questions = tokenizer.decode(outputs[0])
  return paraphrased_questions


# Function to paraphrase a batch of questions
def paraphrase_questions(questions: list[str], model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> List[str]:
  """
  Paraphrases a list of questions using a language model.

  Args:
      questions (List[str]): List of original questions to paraphrase.
      model (PreTrainedModel): The pre-trained language model for generation.
      tokenizer (PreTrainedTokenizer): The tokenizer associated with the model.

  Returns:
      List[str]: List of paraphrased questions.
  """
  
  paraphrased_questions = []
  for question in questions:
      paraphrased_question = paraphrase_question(question, model, "10", 150)
      paraphrased_questions.append(re.search(r'(?<=<start_of_turn>model)(.*)', paraphrased_question, re.DOTALL).group(1))
  return paraphrased_questions

# Function to paraphrase a answers
def paraphrase_answer(answer: str, model: PreTrainedModel, amount: int, max_new_tokens: int) -> str:
  """
  Paraphrases a given answer multiple times using a language model.

  Args:
      answer (str): The original answer to paraphrase.
      model (PreTrainedModel): The pre-trained language model for generation.
      tokenizer (PreTrainedTokenizer): The tokenizer associated with the model.
      amount (int): The number of paraphrased answers to generate.
      max_new_tokens (int): The maximum number of new tokens to generate.

  Returns:
      str: A string containing the paraphrased answers separated by newlines.
  """

  chat = [
    { "role": "user", "content": f"Rephrase the following answer {amount} times: '{answer}'" },
  ]
  prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
  inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
  outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=max_new_tokens, do_sample=True)
  paraphrased_answers = tokenizer.decode(outputs[0])
  return paraphrased_answers


# Function to paraphrase a batch of answers
def paraphrase_answers(answers: list, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> list:
  """
  Paraphrases a list of answers using a language model.

  Args:
      answers (list): A list of dictionaries containing answers to paraphrase.
                      Each dictionary should have a 'text' key with a list of strings as its value.
      model (PreTrainedModel): The pre-trained language model for generation.
      tokenizer (PreTrainedTokenizer): The tokenizer associated with the model.

  Returns:
      list: A list of paraphrased answers.
  """
  
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
