from transformers import AutoModelForCausalLM
from peft import PeftModel
import os

HF_TOKEN = os.getenv('HF_TOKEN', 'add_hf_token')
base_model_name = "google/gemma-2b-it"
adapter_model_name = "julioc-p/DeepCNCFGemma2B"
repo_id = "julioc-p/CNCF"
model = AutoModelForCausalLM.from_pretrained(base_model_name)
model = PeftModel.from_pretrained(model, adapter_model_name)

model = model.merge_and_unload()
model.push_to_hub(repo_id, token=HF_TOKEN)
