# imports
import gc
from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          TrainingArguments,
                          BitsAndBytesConfig
                          )
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from datasets import load_dataset
from huggingface_hub import HfApi, login
import torch
import CustomSFTTrainer
import random
import os
HF_TOKEN = os.getenv('HF_TOKEN', 'add_hf_token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)

gc.collect()
torch.cuda.empty_cache()
# defining hyperparameter search space for optuna


def optuna_hp_space(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 3, 15),
        "weight_decay": trial.suggest_loguniform("weight_decay", 1e-6, 1e-2),
    }

# Define a function to calculate BLEU score


# configuration arguments
model_id = "google/gemma-2-9b-it"

# bits and bytes config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)


def model_init(trial):
    model = AutoModelForCausalLM.from_pretrained(
        model_id, quantization_config=bnb_config, device_map="auto")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)
    return model


# tokenizer load
tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side='right')

dataset = load_dataset(
    "Kubermatic/cncf-question-and-answer-dataset-for-llm-training", split="train")

random.seed(42)
random_indices = random.sample(range(len(dataset)), k=500)

training_indices = random_indices[:400]
eval_indices = random_indices[400:500]
training_dataset = dataset.filter(
    lambda _, idx: idx in training_indices, with_indices=True)
eval_dataset = dataset.filter(
    lambda _, idx: idx in eval_indices, with_indices=True)

max_seq_length = 1024


output_dir = "trained_model"
training_arguments = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
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


# Passing model
model = model_init(None)


# instantiation of the trainer
trainer = CustomSFTTrainer(
    model=model,
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
