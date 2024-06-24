"""
This script demonstrates parallel processing using multithreading to generate questions from chunks of data
using the TransformersQG class from the 'lmqg' library. It loads a dataset from the Hugging Face Datasets library,
iterates over each chunk of data in parallel, and uses a question generation model to produce questions and answers.
The results are appended to a 'questions.csv' file, formatted with columns for Question, Answer, and Project.

Libraries Used:
- datasets: For loading the dataset.
- lmqg: For using the TransformersQG class for question generation.
- threading: For managing concurrent execution of data processing.
- pyparsing: For managing a deque data structure.

Global Variables:
- MAX_THREADS: Defines the maximum number of threads for concurrent processing.
- q: A deque to manage instances of the TransformersQG class.

Steps:
1. Load the dataset "Kubermatic/cncf-raw-data-for-llm-training" from Hugging Face Datasets, specifically the 'train' split.
2. Initialize the 'questions.csv' file with headers for Question, Answer, and Project.
3. Populate the deque 'q' with instances of TransformersQG initialized for question generation.
4. Iterate through each date in the dataset, where each date contains 'content' chunks.
5. Use threading.Semaphore to limit concurrent access to the deque 'q' and ensure thread safety.
6. Create and start a thread for each chunk of content in a date, with each thread invoking process_chunk().
7. Within process_chunk(), retrieve a model instance from 'q', generate questions and answers for the chunk's data using generate_qa(),
   and append the results to 'questions.csv' under the appropriate columns.
8. Print the generated questions and answers for each chunk.
9. Append the model instance back to the deque 'q' after processing.
10. Wait for all threads to complete using thread.join().

Example usage:
Run the script to concurrently process chunks of data from the specified dataset, generate questions and answers using multiple threads,
and save the results in 'questions.csv'.
"""

from datasets import load_dataset
from lmqg import TransformersQG
import threading
from pyparsing import deque


MAX_THREADS = 4
q = deque()


def process_chunk(date: dict[str, dict[str, str]], chunk: dict[str, str], semaphore: Semaphore) -> None:
    """
    Process a chunk of data to generate questions and answers using a model.

    Args:
        date (dict): Dictionary containing date information with 'tag' key.
        chunk (dict): Dictionary representing the chunk of data to process.
        semaphore (Semaphore): Semaphore to control concurrent access.

    Returns:
        None
    """
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
