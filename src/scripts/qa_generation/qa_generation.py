from datasets import load_dataset
from lmqg import TransformersQG
import threading
from pyparsing import deque


MAX_THREADS = 4
q = deque()


def process_chunk(date, chunk, semaphore):
    with semaphore:
        context = f"{chunk['data']}"
        model = q.popleft()
        try:
            qa = model.generate_qa(context)
        except ValueError:
            q.append(model)
            return
        with open("questions.csv", "a") as f:
            for question, answer in qa:
                f.write(
                    f"{question}; {answer}; {date['tag']['project_name']}\n")
        print(qa)
        q.append(model)


dataset = load_dataset(
    "Kubermatic/cncf-raw-data-for-llm-training", split="train")
with open("questions.csv", "w") as f:
    f.write("Question; Answer; Project\n")


for i in range(MAX_THREADS):
    q.append(TransformersQG(language="en",
             model="lmqg/t5-base-squad-qag", drop_overflow_error_text=True))
for date in dataset:
    semaphore = threading.Semaphore(MAX_THREADS)
    threads = []
    for chunk in date["content"]:
        thread = threading.Thread(
            target=process_chunk, args=(date, chunk, semaphore))

        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
