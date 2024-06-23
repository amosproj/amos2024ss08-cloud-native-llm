# This script collects question and answer data from StackOverflow for a list of specified tags. The script uses several 
# libraries to manage API requests, parse HTML, handle JSON and CSV files, and manage threading and multiprocessing. 
# It maintains the progress of processed tags and question IDs, and ensures data consistency with thread-safe operations.

# Key functionalities
# 1. Fetching data from the StackOverflow API with exponential backoff to handle rate limiting.
# 2. Extracting questions and answers for specific tags, ensuring unique processing of question IDs.
# 3. Removing HTML tags from the text for better readability.
# 4. Saving the extracted data to CSV files and maintaining progress in JSON files to resume operations efficiently.
# 5. Concurrently processing multiple tags using a thread pool executor to speed up data collection.

# Dependencies:
# - yaml
# - requests
# - pandas
# - BeautifulSoup
# - time
# - json
# - os
# - sys
# - datetime
# - dotenv
# - concurrent.futures
# - threading
# - multiprocessing

# Modules:
# - `fetch_with_backoff(api_url, params)`: Fetches data from the API with retry logic.
# - `qa_extractor(tag, start_page, page_size)`: Extracts questions for a given tag.
# - `fetch_answers(question_id)`: Fetches answers for a specific question.
# - `remove_html_tags(text)`: Removes HTML tags from the text.
# - `extract_all_projects(tags)`: Manages the extraction process for multiple tags concurrently.
# - `save_to_csv(data, filename)`: Saves data to a CSV file.
# - `load_progress()`: Loads progress from a JSON file.
# - `save_progress(tag, page)`: Saves progress to a JSON file.
# - `load_processed_question_ids()`: Loads processed question IDs from a JSON file.
# - `save_processed_question_ids(processed_ids)`: Saves processed question IDs to a JSON file.
# - `load_tags()`: Loads tags from a YAML file or a cached JSON file, updating as necessary.

# Usage:
# - Set the required API key in an .env file.
# - Ensure the necessary directories and files exist or will be created.
# - Run the script to start collecting StackOverflow Q&A data for specified tags.

import yaml
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import multiprocessing

load_dotenv()
API_KEY = os.getenv('API_KEY', 'Replace your api key')
REQUEST_DELAY = 0  # Number of seconds to wait between requests
PROGRESS_FILE = 'sources/stackoverflow_Q&A/stackoverflow_progress.json'
CSV_FILE = 'sources/stackoverflow_Q&A/cncf_stackoverflow_qas.csv'
PROCESSED_IDS_FILE = 'sources/stackoverflow_Q&A/processed_question_ids.json'
TAGS_FILE = 'sources/stackoverflow_Q&A/tags.json'
TAGS_UPDATE_INTERVAL = 7  # Number of days between tag updates
DAILY_REQUEST_LIMIT = 9000
MAX_THREADS = multiprocessing.cpu_count() * 2 
# MAX_THREADS = 10

lock = threading.Lock()  # Initialize a threading lock

def fetch_with_backoff(api_url: str, params: dict) -> dict:
    """Fetch data from the API with exponential backoff for rate limiting.

    Args:
        api_url (str): The API endpoint URL.
        params (dict): Dictionary of query parameters for the API request.

    Returns:
        dict: The JSON response data from the API if successful.
        None: If the API request fails.
    """
    while True:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Waiting for retry...")
            retry_after = int(response.headers.get('retry-after', REQUEST_DELAY))
            time.sleep(retry_after)
            sys.exit()
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            sys.exit()
            return None

def qa_extractor(tag: str, start_page: int, page_size: int = 100) -> int:
    """Fetch questions from StackOverflow for a given tag.

    Args:
        tag (str): The tag to search for on StackOverflow.
        start_page (int): The starting page number for the API request.
        page_size (int, optional): Number of results per page. Defaults to 100.
        

    Returns:
        int: Updated request count after fetching questions.
    """
    api_url = "https://api.stackexchange.com/2.3/search/advanced"
    questions = []
    
    processed_question_ids = load_processed_question_ids()
    request_count = 0
    
    while True:
        if request_count >= DAILY_REQUEST_LIMIT:
            break
        
        params = {
            'page': start_page,
            'pagesize': page_size,
            'order': 'desc',
            'sort': 'activity',
            'answers': 1,
            'tagged': tag,
            'site': 'stackoverflow',
            'filter': 'withbody',
            'key': API_KEY
        }
        
        response_data = fetch_with_backoff(api_url, params)
        request_count += 1
        
        if not response_data or not response_data['items']:
            save_progress(tag, "null")
            break
        
        QA_list = []
        if response_data:
            questions.extend(response_data['items'])
            
            for question in response_data['items']:
                question_id = question['question_id']
                if question_id in processed_question_ids:
                    continue
                if question['answer_count'] > 0:
                    question_text = remove_html_tags(question['body'])
                    answers = fetch_answers(question_id)
                    
                    for count, answer in enumerate(answers, start=1):
                        if count > 3:
                            break
                        if answer['score'] < 0:
                            continue
                        answer_text = remove_html_tags(answer['body'])
                    
                        QA_list.append({
                            "question": question_text,
                            "answer": answer_text,
                            "tag": tag,
                        })
                    
                    processed_question_ids.add(question_id)
                    
            print(f"Fetched {len(response_data['items'])} questions from page {start_page} for tag '{tag}'. Total so far: {len(questions)}")
            save_to_csv(QA_list, CSV_FILE)
            save_processed_question_ids(processed_question_ids)
            
            has_more = response_data.get('has_more', False)
            if not has_more:
                save_progress(tag, "finished")
                break
            
            start_page += 1
            save_progress(tag, start_page)
            time.sleep(REQUEST_DELAY)
        else:
            break
        if request_count >= DAILY_REQUEST_LIMIT:
            break
    
    print(f"Request count for question is: {request_count}")
    return request_count

def fetch_answers(question_id: int) -> list:
    """Fetch answers for a specific question from StackOverflow.

    Args:
        question_id (int): The ID of the question to fetch answers for.

    Returns:
        list: List of answer items if successful, otherwise an empty list.
    """
    api_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        'order': 'desc',
        'sort': 'votes',
        'site': 'stackoverflow',
        'filter': 'withbody',
        'key': API_KEY
    }
    
    response_data = fetch_with_backoff(api_url, params)
    return response_data['items'] if response_data else []

def remove_html_tags(text: str) -> str:
    """Remove HTML tags from a given text.

    Args:
        text (str): The HTML text to be processed.

    Returns:
        str: The text with HTML tags removed.
    """
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def extract_all_projects(tags: List[str]) -> None:
    """Extract QA pairs for multiple tags.

    Args:
        tags (List[str]): List of tags to process.

    Returns:
        None
    """
    progress = load_progress()
    all_tags_done = True
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for tag in tags:
            if progress.get(tag) == "null" or progress.get(tag) == "finished": 
                continue
            else: 
                all_tags_done = False
                start_page = progress.get(tag, 1)
                futures.append(executor.submit(qa_extractor, tag, start_page))
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error occurred: {e}")
                
    if all_tags_done:
        print("We have reached all question-answer data from StackOverflow.")

def save_to_csv(data: List[dict], filename: str) -> None:
    """
    Save a list of dictionaries to a CSV file.

    Args:
        data (List[dict]): The data to be saved.
        filename (str): The name of the CSV file.

    Returns:
        None
    """
    with lock:  # Ensure only one thread writes to the file at a time
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                df = pd.read_csv(filename)
                df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data)
        df.to_csv(filename, index=False)

def load_progress() -> dict:
    """Load progress data from file.

    Returns:
        dict: Dictionary containing progress data.
    """
    try:
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_progress(tag: str, page: str) -> None:
    """
    Save the progress of processing a specific tag.

    Args:
        tag (str): The tag being processed.
        page (str): The current page number.

    Returns:
        None
    """
    with lock:  # Ensure only one thread writes to the file at a time
        progress = load_progress()
        progress[tag] = page
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f)


def load_processed_question_ids() -> set:
    """Load processed question IDs from file.

    Returns:
        set: Set of processed question IDs.
    """
    try:
        if os.path.getsize(PROCESSED_IDS_FILE) == 0:
            return set()
        with open(PROCESSED_IDS_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        return set()

def save_processed_question_ids(processed_ids: set):
    """Save processed question IDs to file.

    Args:
        processed_ids (set): Set of processed question IDs.
    """
    with lock:  # Ensure only one thread writes to the file at a time
        with open(PROCESSED_IDS_FILE, 'w') as f:
            json.dump(list(processed_ids), f)

def load_tags() -> list:
    """Load tags from the JSON file if it's not older than the update interval, otherwise from the YAML file.

    Returns:
        list: List of tags.
    """
    if os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, 'r') as f:
            tags_data = json.load(f)
            last_update = datetime.strptime(tags_data['last_update'], "%Y-%m-%d")
            if datetime.now() - last_update < timedelta(days=TAGS_UPDATE_INTERVAL):
                return tags_data['tags']
    
    with open("amos2024ss08-cloud-native-llm/landscape_augmented_repos_websites.yml", 'r') as f:
        data = yaml.safe_load(f)
    
    tags = []
    tags_dict = {'Project_name': ""}
    for category in data['landscape']:
        category_list = ["App Definition and Development", "Orchestration & Management", "Runtime", \
                        "Provisioning", "Observability and Analysis", "Test_Provisioning"]
        if category['name'] not in category_list:
            continue
        tags_dict['Category'] = category['name']
        for subcategory in category.get('subcategories', []):
            for item in subcategory.get('items', []):
                project_name = item['name'].split('(')[0].strip()
                tags_dict['Project_name'] = project_name
                tags.append(tags_dict['Project_name']) 
    
    tags_data = {
        'tags': tags,
        'last_update': datetime.now().strftime("%Y-%m-%d")
    }
    with open(TAGS_FILE, 'w') as f:
        json.dump(tags_data, f)
    
    return tags

if __name__ == "__main__":
    folder_path = 'sources/stackoverflow_Q&A'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    tags = load_tags()
    
    extract_all_projects(tags)
