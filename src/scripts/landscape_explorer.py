from collections import defaultdict
import requests
import os
import yaml
from tqdm import tqdm
import requests_cache


TOKEN = os.environ['GITHUBTOKEN']
HEADERS = {'Authorization': f'Bearer {TOKEN}',
           'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
BASE_API_URL = 'https://api.github.com'
BASE_REPO_YAML = 'https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml'
EXTENSIONS = ["yml", "yaml", "pdf", "md"]


# Cache requests for 7 days
requests_cache.install_cache('landscape_cache', expire_after=604800)


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
    if not default_branch:
        return {}
    # get tree response
    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{default_branch}?recursive=1'
    response = requests.get(url, headers=HEADERS).json()
    if response.get('truncated'):
        print("Truncated response handled")
        res = defaultdict(list)
        get_urls_recursive(repo_url, default_branch, default_branch, res)
        return res
    #
    tree = response.get('tree')
    if not tree:
        return {}
    # select of type blob and if the extension is in the list
    res = defaultdict(list)
    base_download_url = f'https://raw.githubusercontent.com/{repo_url.split("https://github.com/")[1]}/{default_branch}/'
    for file in tree:
        ext = file.get('path').split('.')[-1]
        if file.get('type') == 'blob' and ext in EXTENSIONS:
            res[ext].append(base_download_url + file.get('path'))
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

    try:
        response = requests.get(
            url, headers=HEADERS)
    except requests.exceptions.RequestException as e:
        print(e)

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return ""

    return response.json().get('default_branch')


def get_augmented_yml_with_urls():
    """
    Retrieves the YAML content from BASE_REPO_YAML, augments it with download URLs,
    and saves the augmented content to 'sources/landscape_augmented.yml'.

    Returns:
        None
    """
    response = requests.get(BASE_REPO_YAML)

    content = response.content.decode('utf-8')
    content = yaml.safe_load(content)  # type dict
    os.makedirs('sources', exist_ok=True)
    for category in tqdm(content.get('landscape')):
        for subcategory in tqdm(category.get('subcategories')):
            for item in tqdm(subcategory.get('items')):
                if 'repo_url' not in item or not item.get('repo_url'):
                    continue
                urls = get_urls(item.get('repo_url'))
                item['download_urls'] = {}
                for ext, url_list in urls.items():
                    item['download_urls'][ext] = url_list
    with open('sources/landscape_augmented.yml', 'w+') as file:
        yaml.dump(content, file, sort_keys=False)


def get_urls_recursive(repo_url: str, default_branch: str, tree_sha, res) -> None:
    print("Recursive call with url: ", repo_url,
          " and tree_sha: ", tree_sha)

    if not default_branch:
        return
    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{tree_sha}'
    try:
        response = requests.get(url, headers=HEADERS)
        response = response.json()
    except Exception as e:
        print(e)
        # print("content of response: ", response.content)
        return

    tree = response.get('tree')

    if not tree:
        return

    base_download_url = f'https://raw.githubusercontent.com/{repo_url.split("https://github.com/")[1]}/{default_branch}/'
    for file in tree:
        if file.get('type') == 'tree':
            get_urls_recursive(repo_url, default_branch, file.get('sha'), res)

        ext = file.get('path').split('.')[-1]
        if file.get('type') == 'blob' and ext in EXTENSIONS:
            res[ext].append(base_download_url + file.get('path'))


if __name__ == '__main__':
    get_augmented_yml_with_urls()
