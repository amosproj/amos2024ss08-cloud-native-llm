from datasets import load_dataset
from lmqg import TransformersQG
import threading


MAX_THREADS = 32


def process_chunk(date, chunk):
    semaphore.acquire()
    context = f"Project: {date['tag']['project_name']}\n{chunk['heading']}\n{chunk['data']}"
    context = context[:1024]
    # print(context)
    model = TransformersQG(language="en", model="lmqg/t5-base-squad-qag")
    qa = model.generate_qa(context)
    with open("questions.csv", "a") as f:
        for question, answer in qa:
            f.write(
                f"{question}; {answer}; {date['tag']['project_name']}\n")
    print(qa)
    semaphore.release()


dataset = load_dataset(
    data_files='Kubermatic/cncf-raw-data-for-llm-training', split="train")
with open("questions.csv", "w") as f:
    f.write("Question; Answer; Project\n")

for date in dataset:
    semaphore = threading.Semaphore(MAX_THREADS)
    threads = []
    for chunk in date["content"]:
        thread = threading.Thread(target=process_chunk, args=(date, chunk))

        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
