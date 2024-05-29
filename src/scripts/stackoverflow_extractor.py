import yaml
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json

API_KEY = ''  # Replace with your actual API key
REQUEST_DELAY = 10  # Number of seconds to wait between requests
CACHE_FILE = 'sources/stackoverflow_cache.json'

def fetch_with_backoff(api_url, params):
    """Fetch data from the API with exponential backoff for rate limiting."""
    while True:
        #print(f"Fetching data with params: {params}")
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Waiting for retry...")
            retry_after = int(response.headers.get('retry-after', REQUEST_DELAY))
            print("Retry after " + str(retry_after))
            time.sleep(retry_after)
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            return None

def fetch_stackoverflow_questions(tag, search_term, page_size=5, max_pages=2):
    """Fetch questions from StackOverflow for a given tag and search term."""
    api_url = "https://api.stackexchange.com/2.3/search/advanced"
    questions = []
    
    for page in range(1, max_pages + 1):
        params = {
            'page': page,
            'pagesize': page_size,
            'order': 'desc',
            'sort': 'activity',
            'tagged': tag,
            #'q': search_term,
            'site': 'stackoverflow',
            'filter': 'withbody',  # Ensuring the 'body' field is included
            #'key': API_KEY
        }
        
        response_data = fetch_with_backoff(api_url, params)
        if response_data:
            questions.extend(response_data['items'])
            has_more = response_data.get('has_more', False)
            if not has_more:
                break
            print(f"Fetched {len(response_data['items'])} questions from page {page} for tag '{tag}' with search term '{search_term}'. Total so far: {len(questions)}")
            time.sleep(REQUEST_DELAY)  # Add delay between requests to avoid rate limiting
        else:
            break
    
    return questions

def fetch_answers(question_id):
    """Fetch answers for a specific question from StackOverflow."""
    api_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        'order': 'desc',
        'sort': 'votes',
        'site': 'stackoverflow',
        'filter': 'withbody',  # Ensuring the 'body' field is included
        #'key': API_KEY
    }
    
    response_data = fetch_with_backoff(api_url, params)
    if response_data:
        return response_data['items']
    else:
        print(f"Failed to fetch answers for question {question_id}")
        return []

def remove_html_tags(text):
    """Remove HTML tags from a given text."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def qa_extractor(tag, search_terms, max_answer_number=3):
    """Extract questions and their top answers for a given tag and search terms."""
    all_questions = []
    
    for search_term in search_terms:
        questions = fetch_stackoverflow_questions(tag, search_term)
        all_questions.extend(questions)
    
    QA_list = []
    
    for question in all_questions:
        # checks if the question has any answer
        if question['answer_count'] > 0:
            question_text = remove_html_tags(question['body'])
            answers = fetch_answers(question['question_id'])
            formatted_answers = []
            
            for count, answer in enumerate(answers, start=1):
                # only consicer a specifice number of answers with the highest vot, not all of them
                if count > max_answer_number:
                    break
                # if the answer has a negetive score ignore it
                if answer['score'] < 0:
                    continue
                answer_text = remove_html_tags(answer['body'])
                formatted_answers.append(f"{count}. {answer_text}")
                
            #QA_list.append({"question" : question['body'], "answer" : answer['body'] })
            QA_list.append({
                "question": question_text,
                "answer": "\n".join(formatted_answers),
                 "tag": tag,
            })
    
    return QA_list

def extract_all_projects(tags, search_terms):
    """Extract QA pairs for multiple tags and search terms."""
    all_qas = []
    for tag in tags:
        print(f"Extracting Q&A for tag: {tag} with search terms: {search_terms}")
        qas = qa_extractor(tag, search_terms)
        all_qas.extend(qas)
    
    return all_qas

def save_to_csv(data, filename):
    """Save extracted data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def load_cache():
    """Load cached data from file."""
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    """Save data to cache file."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    with open("sources/landscape_augmented_repos_websites.yml", 'r') as f:
        data = yaml.safe_load(f)

    tags = []

    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {'Project_name': ""}
    # Process the loaded data
    for category in data['landscape']:
        # It downloads only below defined categories to avoid duplication
        category_list = ["App Definition and Development", "Orchestration & Management", "Runtime", \
                        "Provisioning", "Observability and Analysis", "Test_Provisioning"]
        if category['name'] not in category_list:
            continue
        tags_dict['Category'] = category['name']
        for subcategory in category.get('subcategories', []):
            for item in subcategory.get('items', []):
                # Remove brackets from project name
                project_name = item['name'].split('(')[0].strip()
                tags_dict['Project_name'] = project_name
                tags.append(tags_dict['Project_name'])         

    search_terms = ['CNCF', 'cncf', 'Cloud Native Computing Foundation']   
    # Load cached data
    cache = load_cache()
    
    all_qas = extract_all_projects(tags, search_terms)
    
    # Update cache with new data
    for qa in all_qas:
        cache[qa['question']] = qa
    
    # Save cache
    save_cache(cache)
    
    save_to_csv(all_qas, "sources/cncf_stackoverflow_qas.csv")







