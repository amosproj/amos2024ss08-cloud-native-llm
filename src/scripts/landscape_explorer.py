from collections import defaultdict
import requests
import os
import sys

TOKEN = os.environ['GITHUBTOKEN']
HEADERS = {'Authorization': f'{TOKEN}',
           'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
BASE_API_URL = 'https://api.github.com'
BASE_REPO_YAML = 'https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml'
EXTENSIONS = ["yml", "yaml", "pdf", "md"]


def get_urls(repo_url: str) -> dict:
    """
    Retrieves the URLs of files with specified extensions from a GitHub repository.

    Args:
        extensions (list): A list of file extensions to filter the URLs.
        repo_url (str): The URL of the GitHub repository.

    Returns:
        dict: A dictionary where the keys are the file extensions and the values are lists of URLs.

    """
    default_branch = get_default_branch(repo_url)
    # get tree response
    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{default_branch}?recursive=1'
    response = requests.get(url, headers=HEADERS).json()
    # if response.get('truncated'):
    # TODO: Handle case where response is truncated (more than 100000 registers)
    #
    tree = response.get('tree')
    # select of type blob and if the extension is in the list
    res = defaultdict(list)
    base_download_url = f'https://raw.githubusercontent.com/{repo_url.split("https://github.com/")[1]}/{default_branch}/'
    for file in tree:
        ext = file.get('path').split('.')[-1]
        if file.get('type') == 'blob' and ext in EXTENSIONS:
            res[ext].append(base_download_url + file.get('path'))
    return res


def get_default_branch(repo_url):

    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}'

    try:
        response = requests.get(
            url, headers=HEADERS)
    except requests.exceptions.RequestException as e:
        print(e)

    return response.json().get('default_branch')


if __name__ == '__main__':

    get_urls(sys.argv[1])
