import requests
import json
import os
import sys

TOKEN = os.environ['GITHUBTOKEN']
HEADERS = {'Authorization': f'{TOKEN}',
           'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
BASE_URL = 'https://api.github.com'


def get_urls(extensions, repo_url):

    default_branch = get_default_branch(repo_url)
    # get tree response
    url = f'{BASE_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{default_branch}?recursive=1'
    print(url)
    response = requests.get(url, headers=HEADERS)
    print(response.json())


def get_default_branch(repo_url):

    url = f'{BASE_URL}/repos/{repo_url.split("https://github.com/")[1]}'

    try:
        response = requests.get(
            url, headers=HEADERS)
    except requests.exceptions.RequestException as e:
        print(e)

    return response.json().get('default_branch')


if __name__ == '__main__':
    get_urls(sys.argv[1], sys.argv[2])
