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
    # get tree response
    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}/git/trees/{default_branch}?recursive=1'
    response = requests.get(url, headers=HEADERS).json()
    if response.get('truncated'):
        print('Response is truncated')
    # TODO: Handle case where response is truncated (more than 100000 registers)
    #
    tree = response.get('tree')  # TODO: Handle case where tree is null
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


def get_default_branch(repo_url):

    url = f'{BASE_API_URL}/repos/{repo_url.split("https://github.com/")[1]}'

    try:
        response = requests.get(
            url, headers=HEADERS)
    except requests.exceptions.RequestException as e:
        print(e)

    if response.status_code != 200:
        print(f'Error: {response.status_code}')
        return None

    return response.json().get('default_branch')


def get_augmented_yml_with_urls():
    response = requests.get(BASE_REPO_YAML)

    content = response.content.decode('utf-8')
    content = yaml.safe_load(content)  # type dict
    # number_files = 5
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
                # number_files -= 1
                # if not number_files:
                #     with open('sources/landscape_augmented.yml', 'w+') as file:
                #         yaml.dump(content, file, sort_keys=False)
                #     sys.exit(0)
    with open('sources/landscape_augmented.yml', 'w+') as file:
        yaml.dump(content, file, sort_keys=False)


if __name__ == '__main__':
    get_augmented_yml_with_urls()
