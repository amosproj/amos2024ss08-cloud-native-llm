# imports
from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          TrainingArguments,
                          BitsAndBytesConfig
                          )
from trl import SFTTrainer
from peft import LoraConfig
from datasets import load_dataset
from huggingface_hub import HfApi, login
import torch

import os
HF_TOKEN = os.getenv('HF_TOKEN', 'add_hf_token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)


# defining hyperparameter search space for optuna


def optuna_hp_space(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True),
        "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", [16, 32, 64]),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 3, 15),
        "weight_decay": trial.suggest_loguniform("weight_decay", 1e-6, 1e-2),
    }

# Define a function to calculate BLEU score


# configuration arguments
model_id = "google/gemma-2-27b-it"

# bits and bytes config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)


def model_init(trial):
    return AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map="auto",)


# tokenizer load
tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side='right')

# Loading training and evaluation data
training_dataset = load_dataset(
    "Kubermatic/cncf-question-and-answer-dataset-for-llm-training", split="train[:7500]")
eval_dataset = load_dataset(
    "Kubermatic/cncf-question-and-answer-dataset-for-llm-training", split="train[7500:8000]")

max_seq_length = 1024


output_dir = "trained_model"
training_arguments = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=1,
    gradient_checkpointing=True,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    optim="paged_adamw_32bit",
    save_steps=0,
    logging_steps=10,
    learning_rate=5e-4,
    weight_decay=0.001,
    fp16=True,
    bf16=False,
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=False,
    evaluation_strategy='steps',
    eval_steps=500,
    eval_accumulation_steps=1,
    lr_scheduler_type="cosine",
    report_to="tensorboard",
    disable_tqdm=True,
    # debug="underflow_overflow"
)

lora_config = LoraConfig(
    lora_alpha=64,
    lora_dropout=0.1,
    r=32,
    bias="none",
    target_modules=["q_proj", "o_proj", "k_proj",
                    "v_proj", "gate_proj", "up_proj", "down_proj"],
    # TODO: Check if this can be changed to QUESTION_ANS with GEMMA
    task_type="CAUSAL_LM",
)

# formatting function


def formatting_func(example):
    output_texts = []
    for i in range(len(example['Question'])):
        text = f"### Question: {example['Question'][i]}\n ### Answer: {example['Answer'][i]}<eos>"
        output_texts.append(text)
    return output_texts

# instantiation of the trainer


trainer = SFTTrainer(
    model=model_id,
    train_dataset=training_dataset,
    eval_dataset=eval_dataset,
    args=training_arguments,
    peft_config=lora_config,
    formatting_func=formatting_func,
    tokenizer=tokenizer,
    max_seq_length=max_seq_length,
    model_init=model_init,
)

# avoid placing model on device as it is already placed on device in model_init
trainer.place_model_on_device = False

best_trial = trainer.hyperparameter_search(
    direction="minimize",
    hp_space=optuna_hp_space,
    n_trials=20,
)

print(best_trial)
