import requests

def fetch_stackoverflow_questions(tag, pages=1, pagesize=10):
    api_url = "https://api.stackexchange.com/2.3/questions"
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    questions = []
    
    for page in range(1, pages + 1):
        params = {
            'page': page,
            'pagesize': pagesize,
            'order': 'desc',
            'sort': 'activity',  # Sort by most viewed
            'tagged': tag,
            'site': 'stackoverflow',
            'filter': 'withbody',  # Include body in the response
            # Filter only questions with at least one answer
            #'key': api_key,
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            questions.extend(data['items'])
        else:
            print(f"Failed to fetch data: {response.status_code}")
            print(response.headers)
            break
    
    return questions

def fetch_answers(question_id):
    api_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    params = {
        'order': 'desc',
        'sort': 'votes',  # Sort answers by highest votes
        'site': 'stackoverflow',
        'filter': 'withbody'  # Include body in the response
        #'key': api_key
    }
    
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print(f"Failed to fetch answers for question {question_id}: {response.status_code}")
        return []
def qa_exctractor():
    tag = "kubernetes"
    max_answer_number = 3
    questions = fetch_stackoverflow_questions(tag, pages=2, pagesize=5)
    QA_list = []
    for question in questions:
        #checks if the question has any answer
        if question['answer_count'] > 0:
            print(f"Title: {question['title']}")
            print(f"Link: {question['link']}")
            #print(f"Link: {question['body']}")
            # Fetch and list answers
            answers = fetch_answers(question['question_id'])
            print("Answers:")
            for count, answer in enumerate(answers, start=1):
                # only consicer a specifice number of answers with the highest vot, not all of them
                if count > max_answer_number:
                    break
                #print(f"  - Score: {answer['score']}, Body: {answer['body']}")
                # if the answer has a negetive score ignore it
                if answer['score'] < 0:
                    continue
                QA_list.append({"question" : question['body'], "answer" : answer['body'] })
    return QA_list
    
# Example usage
if __name__ == "__main__":
    qa_exctractor()