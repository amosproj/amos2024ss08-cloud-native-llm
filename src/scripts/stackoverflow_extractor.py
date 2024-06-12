import yaml
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import os
import sys
from datetime import datetime, timedelta

API_KEY = ''  # Replace with your actual API key of stackexchange
REQUEST_DELAY = 0  # Number of seconds to wait between requests
PROGRESS_FILE = 'sources/stackoverflow_progress.json'
CSV_FILE = 'sources/cncf_stackoverflow_qas.csv'
PROCESSED_IDS_FILE = 'sources/processed_question_ids.json'
TAGS_FILE = 'sources/tags.json'
TAGS_UPDATE_INTERVAL = 7  # Number of days between tag updates
DAILY_REQUEST_LIMIT = 9000


def fetch_with_backoff(api_url, params):
    """Fetch data from the API with exponential backoff for rate limiting.

    Args:
        api_url (str): The API endpoint URL.
        params (dict): Dictionary of query parameters for the API request.

    Returns:
        dict: The JSON response data from the API if successful.
        None: If the API request fails.
    """
    while True:
        # print(f"Fetching data with params: {params}")
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Waiting for retry...")
            retry_after = int(response.headers.get('retry-after', REQUEST_DELAY))
            sys.exit()
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            sys.exit()
            return None

def qa_extractor(request_count, tag, start_page, page_size=100,):
    """Fetch questions from StackOverflow for a given tag.

    Args:
        request_count (int): Current count of API requests made.
        tag (str): The tag to search for on StackOverflow.
        start_page (int): The starting page number for the API request.
        page_size (int, optional): Number of results per page. Defaults to 100.
        

    Returns:
        int: Updated request count after fetching questions.
    """

    api_url = "https://api.stackexchange.com/2.3/search/advanced"
    questions = []
    
    # Load processed question IDs
    processed_question_ids = load_processed_question_ids()
    
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
            'filter': 'withbody',  # Ensuring the 'body' field is included
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
                    request_count += 1
                    
                    answers = fetch_answers(question_id)
                    # formatted_answers = []
                    
                    for count, answer in enumerate(answers, start=1):
                        if count > 3:
                            break
                        if answer['score'] < 0:
                            continue
                        answer_text = remove_html_tags(answer['body'])
                        # formatted_answers.append(f"{count}. {answer_text}")
                    
                        QA_list.append({
                            "question": question_text,
                            # "answer": "\n".join(formatted_answers),
                            "answer": answer_text,
                            "tag": tag,
                        })
                    
                    # Add question ID to the set of processed IDs
                    processed_question_ids.add(question_id)
            
            has_more = response_data.get('has_more', False)
            if not has_more:
                save_progress(tag, "finished")
                break
            
            print(f"Fetched {len(response_data['items'])} questions from page {start_page} for tag '{tag}'. Total so far: {len(questions)}")
            save_to_csv(QA_list, CSV_FILE)
            save_processed_question_ids(processed_question_ids)
            start_page += 1
            save_progress(tag, start_page)
            time.sleep(REQUEST_DELAY)  # Add delay between requests to avoid rate limiting
        else:
            break
        if request_count >= DAILY_REQUEST_LIMIT:
            # print(f"Request count is: {request_count}")
            break
    
    print(f"Request count for question is: {request_count}")
    return request_count

def fetch_answers(question_id):
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
        'filter': 'withbody',  # Ensuring the 'body' field is included
        'key': API_KEY
    }
    
    response_data = fetch_with_backoff(api_url, params)
    return response_data['items'] if response_data else []

def remove_html_tags(text):
    """Remove HTML tags from a given text.

    Args:
        text (str): The HTML text to be processed.

    Returns:
        str: The text with HTML tags removed.
    """
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def extract_all_projects(tags, request_count):
    """Extract QA pairs for multiple tags.

    Args:
        tags (list): List of tags to process.
        request_count (int): Initial count of API requests made.
    """
    progress = load_progress()
    all_tags_done = True  # Flag to check if all tags are done
    for tag in tags:
        if progress.get(tag) == "null" or progress.get(tag) == "finished": 
            continue
        else: 
            all_tags_done = False  # Found a tag that needs processing
            start_page = progress.get(tag, 1)
        
        request_count = qa_extractor(request_count, tag, start_page=start_page)
        if request_count >= DAILY_REQUEST_LIMIT:
            break
    if all_tags_done:
        print("We have reached all question-answer data from StackOverflow.")

def save_to_csv(data, filename):
    """Save extracted data to a CSV file.

    Args:
        data (list): List of dictionaries containing QA data.
        filename (str): The filename for the CSV file.
    """
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            df = pd.read_csv(filename)
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    # print(f"Data saved to {filename}")

def load_progress():
    """Load progress data from file.

    Returns:
        dict: Dictionary containing progress data.
    """
    try:
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"File {PROGRESS_FILE} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in {PROGRESS_FILE}.")
        return {}

def save_progress(tag, page):
    """Save progress data to file.

    Args:
        tag (str): The tag being processed.
        page (str or int): The current page number or status.
    """
    progress = load_progress()
    progress[tag] = page
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def load_processed_question_ids():
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

def save_processed_question_ids(processed_ids):
    """Save processed question IDs to file.

    Args:
        processed_ids (set): Set of processed question IDs.
    """
    with open(PROCESSED_IDS_FILE, 'w') as f:
        json.dump(list(processed_ids), f)

def load_tags():
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
    
    # If the JSON file doesn't exist or is older than the update interval, load from YAML
    with open("sourcesl/andscape_augmented.yml", 'r') as f:
        data = yaml.safe_load(f)
    
    tags = []
    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {'Project_name': ""}
    # Process the loaded data
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
    
    # Save the tags to the JSON file with the current date
    tags_data = {
        'tags': tags,
        'last_update': datetime.now().strftime("%Y-%m-%d")
    }
    with open(TAGS_FILE, 'w') as f:
        json.dump(tags_data, f)
    
    return tags

if __name__ == "__main__":
    tags = load_tags()
    request_count = 0
    # Extract and save QA pairs incrementally
    extract_all_projects(tags, request_count)
