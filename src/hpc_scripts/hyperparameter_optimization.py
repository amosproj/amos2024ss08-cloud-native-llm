# imports
import transformers
from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          TrainingArguments,
                          )
from trl import SFTTrainer
from peft import LoraConfig
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import HfApi, login
from transformers.hyperparameter_search import HPSearchBackend
from transformers.trainer import *
import optuna
import gc

import os
HF_TOKEN = os.getenv('HF_TOKEN', 'add_hf_token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)


gc.collect()
torch.cuda.empty_cache()


def run_hp_search_optuna(trainer, n_trials, direction, **kwargs):

    def _objective(trial, checkpoint_dir=None):
        checkpoint = None
        if checkpoint_dir:
            for subdir in os.listdir(checkpoint_dir):
                if subdir.startswith(PREFIX_CHECKPOINT_DIR):
                    checkpoint = os.path.join(checkpoint_dir, subdir)
        #################
        # UPDATES START
        #################
        if not checkpoint:
            # free GPU memory
            del trainer.model
            gc.collect()
            torch.cuda.empty_cache()
        trainer.objective = None
        trainer.train(resume_from_checkpoint=checkpoint, trial=trial)
        # If there hasn't been any evaluation during the training loop.
        if getattr(trainer, "objective", None) is None:
            metrics = trainer.evaluate()
            trainer.objective = trainer.compute_objective(metrics)
        return trainer.objective

    timeout = kwargs.pop("timeout", None)
    n_jobs = kwargs.pop("n_jobs", 1)
    study = optuna.create_study(direction=direction, **kwargs)
    study.optimize(_objective, n_trials=n_trials,
                   timeout=timeout, n_jobs=n_jobs)
    best_trial = study.best_trial
    return BestRun(str(best_trial.number), best_trial.value, best_trial.params)


def hyperparameter_search(
    self,
    hp_space,
    n_trials,
    direction,
    compute_objective=default_compute_objective,
) -> Union[BestRun, List[BestRun]]:

    trainer.hp_search_backend = HPSearchBackend.OPTUNA
    self.hp_space = hp_space
    trainer.hp_name = None
    trainer.compute_objective = compute_objective
    best_run = run_hp_search_optuna(trainer, n_trials, direction)
    self.hp_search_backend = None
    return best_run


transformers.trainer.Trainer.hyperparameter_search = hyperparameter_search


# defining hyperparameter search space for optuna


def optuna_hp_space(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True),
        "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", [16, 32, 64]),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 3, 15),
        "weight_decay": trial.suggest_loguniform("weight_decay", 1e-6, 1e-2),
        "gradient_clipping": trial.suggest_float("gradient_clipping", 0.1, 0.5),
    }

# Define a function to calculate BLEU score


# configuration arguments
model_id = "google/gemma-2-27b-it"

# model init function for the trainer


def model_init(trial):

    return AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")


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

best_trial = trainer.hyperparameter_search(
    direction="minimize",
    hp_space=optuna_hp_space,
    n_trials=20,
)

print(best_trial)
