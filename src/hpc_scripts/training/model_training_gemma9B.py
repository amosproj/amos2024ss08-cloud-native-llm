from transformers import (AutoModelForCausalLM,
                          AutoTokenizer,
                          BitsAndBytesConfig,
                          TrainingArguments
                          )
from trl import SFTTrainer
from peft import LoraConfig
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import HfApi, login
import os
HF_TOKEN = os.getenv('HF_TOKEN', 'add_hf_token')
api = HfApi()
login(HF_TOKEN, add_to_git_credential=True)


# training pipeline taken from https://huggingface.co/blog/gemma-peft
model_id = "google/gemma-2-9b-it"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

dataset = load_dataset(
    "Kubermatic/Merged_QAs", split="train")
dataset.shuffle(42)

tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side='right')
# TODO: Check if this can be changed to AutoModelForQuestionAnswering with GEMMA
model = AutoModelForCausalLM.from_pretrained(
    model_id, quantization_config=bnb_config, device_map="auto", torch_dtype=torch.bfloat16)


# Training (hyper)parameters (initial config taken from: https://medium.com/@lucamassaron/sherlock-holmes-q-a-enhanced-with-gemma-2b-it-fine-tuning-2907b06d2645)
max_seq_length = 1024


output_dir = "output"


training_arguments = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=5,
    gradient_checkpointing=True,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    optim="paged_adamw_32bit",
    save_steps=0,
    logging_steps=10,
    learning_rate=1.344609154868106e-05,
    weight_decay=0.00019307024914471071,
    fp16=False,
    bf16=True,
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=False,
    lr_scheduler_type="cosine",
    report_to="tensorboard",
    disable_tqdm=False,
    # debug="underflow_overflow"
)

text = "### Question: How does the `ScaleWorkload` function facilitate the scaling of a workload to specified replicas?"
device = "cuda:0"
inputs = tokenizer(text, return_tensors="pt").to(device)

outputs = model.generate(**inputs, max_new_tokens=500)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))


def formatting_func(example):
    output_texts = []
    for i in range(len(example['Question'])):
        text = f"### Question: {example['Question'][i]}\n ### Answer: {example['Answer'][i]}<eos>"
        output_texts.append(text)
    return output_texts


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


trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_arguments,
    peft_config=lora_config,
    formatting_func=formatting_func,
    tokenizer=tokenizer,
    max_seq_length=max_seq_length,
)
trainer.train()
print("Model is trained")

text = "### Question: How does the `ScaleWorkload` function facilitate the scaling of a workload to specified replicas?"
device = "cuda:0"
inputs = tokenizer(text, return_tensors="pt").to(device)

outputs = model.generate(**inputs, max_new_tokens=500)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

# Save model
trainer.save_model()
tokenizer.save_pretrained(output_dir)
