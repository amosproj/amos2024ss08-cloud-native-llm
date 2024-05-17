from datasets import load_dataset
from lmqg import TransformersQG

model = TransformersQG(language= "en", model = "lmqg/t5-base-squad-qag")
dataset = load_dataset("Kubermatic/cncf-raw-data-for-llm-training", split = "train")
with open("questions.csv", "w") as f:
    f.write("Question; Answer\n")
for date in dataset:
    for chunk in date["content"]:
        context = f"Project: {date['tag']['project_name']}\n{chunk['heading']}\n{chunk['data']}"
        context = context[:512]
        print(context)
        qa = model.generate_qa(context)
        with open("questions.csv", "a") as f:
            for question, answer in qa:
                f.write(f"{question}; {answer}\n")
        print(qa)
        


