from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          TrainingArguments,
                          )
import pandas as pd
from datasets import load_dataset

from prometheus_eval.vllm import VLLM
from prometheus_eval import PrometheusEval
from prometheus_eval.prompts import RELATIVE_PROMPT

dataset = load_dataset("Kubermatic/Merged_QAs", split = "train[-50:]")
gemma_answers = pd.read_csv("gemma_results.csv")
cncf_answers = pd.read_csv("cncf_results.csv")
llama_answers = pd.read_csv("llama_results.csv")

model = VLLM(model="prometheus-eval/prometheus-7b-v2.0")
judge = PrometheusEval(model=model, relative_grade_template=RELATIVE_PROMPT)

import json

# Create the data structure as per the given example
data_dic = {
    "metadata": [
        {
            "source_path": "First Run",
            "custom_fields_schema": []
        }
    ],
    "models": [
        {"name": "Base Gemma Model 9B"},
        {"name": "Finetuned Model 9B"}
    ],
    "examples": [
    ]
}
for i in range(len(gemma_answers.index)):
  data = {
  "instruction": dataset["Question"][i],
  "response_A": gemma_answers.iloc[i, 0],
  "response_B": cncf_answers.iloc[i, 0],
  "reference_answer": f"{dataset['Question'][i]} \n{dataset['Answer'][i]}",
  "rubric": "Which is the better answer to the question taking into account the reference answer?"
}
    
  feedback, score = judge.single_relative_grade(**data)
  if score == 'A':
    score = -1
  else:
    score = 1
  example = {
            "input_text": dataset["Question"][i],
            "tags": ["CNCF"],  # A list of keywords for categorizing prompts
            "output_text_a": gemma_answers.iloc[i, 0],
            "output_text_b": cncf_answers.iloc[i, 0],
            "score": score,  # Score from the judge LLM
            "individual_rater_scores": [],
            "custom_fields": {}
          }
  data_dic["examples"].append(example)

  print("Feedback:", feedback)
  print("Score:", score)

file_path = "output/prometheus.json"

with open(file_path, 'w') as json_file:
  json.dump(data_dic, json_file, indent=4)
