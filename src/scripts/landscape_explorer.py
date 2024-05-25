#!/usr/bin/python3
from yaml.representer import Representer
from collections import defaultdict
import requests
import os
import yaml
from tqdm import tqdm
import requests_cache
import logging
import time
import collections

# Replace with your GitHub token
TOKEN = os.environ['GITHUB_TOKEN']
if not TOKEN:
    TOKEN = "TEST_TOKEN"
HEADERS = {'Authorization': f'Bearer {TOKEN}',
           'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
BASE_API_URL = 'https://api.github.com'
BASE_REPO_YAML = 'https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml'
EXTENSIONS = ["yml", "yaml", "pdf", "md"]
OUTPUT_PATH = '../../sources/landscape_augmented_repos.yml'

yaml.add_representer(collections.defaultdict, Representer.represent_dict)

# Cache requests for 7 days
requests_cache.install_cache('landscape_cache', expire_after=604800)


def get_urls(repo_url: str, default_branch: str = "", tree_sha: str = "", file_path: str = "", res: defaultdict = None) -> defaultdict:
    """
    Retrieves the URLs of files with specific extensions from a GitHub repository.

    Args:
        repo_url (str): The URL of the GitHub repository.
        default_branch (str, optional): The default branch of the repository. Defaults to "".
        tree_sha (str, optional): The SHA of the tree object. Defaults to "".
        file_path (str, optional): The path to a specific file or directory within the repository. Defaults to "".
        res (defaultdict, optional): A defaultdict to store the URLs of files with specific extensions. Defaults to None.

    Returns:
        defaultdict: A defaultdict containing the URLs of files with specific extensions.

    """
    if res is None:
        res = defaultdict(list)

    if not default_branch:
        default_branch = get_default_branch(repo_url)

    if not tree_sha:
        tree_sha = default_branch

    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{tree_sha}?recursive=1'
    response = make_request(url).json()
    truncated = False
    if response.get('truncated'):
        logging_path = file_path if file_path else "root"
        logging.info(
            f'request for files in path {logging_path} in repository: {repo_url} got truncated because of file number limit')
        truncated = True
        url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{tree_sha}'
        response = make_request(url).json()

    tree = response.get('tree')

    if not tree:
        return res

    base_download_url = f'https://raw.githubusercontent.com/{repo_url.split("https://github.com/")[1]}/{default_branch}/'

    for file in tree:
        ext = file.get('path').split('.')[-1]
        new_file_path = file_path + "/" + \
            file.get('path') if file_path else file.get('path')
        if file.get('type') == 'blob' and ext in EXTENSIONS:
            res[ext].append(base_download_url + new_file_path)

        if truncated and file.get('type') == 'tree':
            get_urls(repo_url, default_branch, file.get(
                'sha'), new_file_path, res)

    return res


def get_default_branch(repo_url: str) -> str:
    """
    Retrieves the default branch of a GitHub repository.

    Args:
        repo_url (str): The URL of the GitHub repository.

    Returns:
        str: The name of the default branch.

    Raises:
        requests.exceptions.RequestException: If there is an error making the HTTP request.

    """
    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}'

    response = make_request(url)

    return response.json().get('default_branch')


def generate_augmented_yml_with_urls():
    """
    Retrieves the YAML content from BASE_REPO_YAML, augments it with download URLs,
    and saves the augmented content to 'sources/landscape_augmented.yml'.

    Returns:
        None
    """
    response = make_request(BASE_REPO_YAML)

    content = response.content.decode('utf-8')
    content = yaml.safe_load(content)  # type dict
    os.makedirs('../../sources', exist_ok=True)
    for category in tqdm(content.get('landscape'), desc="categories"):
        for subcategory in tqdm(category.get('subcategories'), desc="subcategories"):
            for item in tqdm(subcategory.get('items'), desc="sources"):
                if 'repo_url' not in item or not item.get('repo_url'):
                    continue
                urls = get_urls(item.get('repo_url'))
                item['repo'] = defaultdict(defaultdict)
                for ext, url_list in urls.items():
                    item['repo']['download_urls'][ext] = url_list
    with open(OUTPUT_PATH, 'w+') as file:
        yaml.dump(content, file, sort_keys=False)


def make_request(url):
    print("making request to url: ", url)
    response = requests.get(url, headers=HEADERS)
    print(response)
    if 'retry_after' in response.headers:
        logging.warning(
            f'Rate limit exceeded. Retrying after {response.headers["retry-after"]} seconds')
        time.sleep(int(response.headers['retry-after']))
    elif 'x-ratelimit-remaining' in response.headers and int(response.headers['x-ratelimit-remaining']) == 0:
        logging.warning(
            f'Rate limit exceeded. Retrying after {response.headers["x-ratelimit-remaining"]} seconds')
        time.sleep(int(response.headers['x-ratelimit-reset']))

    response = requests.get(url, headers=HEADERS)

    return response


if __name__ == '__main__':
    generate_augmented_yml_with_urls()
