from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          TrainingArguments,
                          )
import pandas as pd
from datasets import load_dataset

from prometheus_eval.vllm import VLLM
from prometheus_eval import PrometheusEval
from prometheus_eval.prompts import RELATIVE_PROMPT

dataset = load_dataset("Kubermatic/cncf-question-and-answer-dataset-for-llm-training", split = "train[:50]")
gemma_answers = pd.read_csv("gemma_results.csv")
cncf_answers = pd.read_csv("cncf_results.csv")

model = VLLM(model="prometheus-eval/prometheus-7b-v2.0")
judge = PrometheusEval(model=model, relative_grade_template=RELATIVE_PROMPT)

for i in range(len(dataset["Question"])):
  data = {
  "instruction": dataset["Question"][i],
  "response_A": gemma_answers.iloc[i, 0],
  "response_B": cncf_answers.iloc[i, 0],
  "reference_answer": f"{dataset['Question'][i]} \n{dataset['Answer'][i]}",
  "rubric": "How similiar is the answer to the reference?"
}


  feedback, score = judge.single_relative_grade(**data)

  print("Feedback:", feedback)
  print("Score:", score)
