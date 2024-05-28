import requests

params = {
            'page': 1,
            'pagesize': 3,
            'order': 'desc',
            'sort': 'activity',
            'tagged': 'kubernetes',
            #'q': search_term,
            'site': 'stackoverflow',
            'filter': 'withbody',  # Ensuring the 'body' field is included
            #'key': API_KEY
        }
api_url = "https://api.stackexchange.com/2.3/search/advanced"
response = requests.get(api_url, params=params)
retry_after = response.headers
print(retry_after)