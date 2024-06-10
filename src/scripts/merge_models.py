from transformers import AutoModelForCausalLM, AutoConfig
from peft import PeftModel

model = AutoModelForCausalLM.from_pretrained("google/gemma-1.1-7b-it")
model = PeftModel.from_pretrained(model, "Kubermatic/DeepCNCF")

model = model.merge_and_unload()
model.save_pretrained("merged_adapters")