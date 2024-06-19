import requests
import yaml
import os
import threading
import langid
import time
import shutil
from requests.exceptions import RequestException
import multiprocessing


# Replace with your GitHub token to increase github API hourly rate to 5000
TOKEN = os.getenv('GITHUB_TOKEN', 'Replace your token')
HEADERS = {'Authorization': f'Bearer {TOKEN}',
           'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}

CACHE_FILE = 'landscape_extractor_cache.txt'


def load_cache():
    """Load the cache from the cache file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()


def save_cache(url):
    """Save the cache to the cache file."""
    with open(CACHE_FILE, 'a') as f:
        f.write(url + '\n')


def isFileEnglish(content):
    try:
        decoded_content = content.decode('utf-8')
        lang, _ = langid.classify(decoded_content)
        return lang == 'en'
    except UnicodeDecodeError as e:
        print("Unicode decode error:", e)
        return False
    except Exception as e:
        print("Cannot understand the language of the file:", e)
        return True


def downloader(url, output_directory, tags_dict, semaphore, cache):
    """
    This function downloads a single file from the url in the input. It is used by downloader_multi_thread() at each thread.
    This function uses a semaphore to control the number of concurrent downloads.
    Args:
        url (str): A single url string.
        output_directory (str): The path where the downloaded files will be stored.
        tags_dict(dict): A dictionary containing the tags for each file. For example: Category, Subcategory, Project_name
        semaphore (threading.Semaphore): A semaphore object used to limit the number of concurrent downloads.
        cache (set): A set to track downloaded files.
    """
    with semaphore:
        if url in cache:
            print(f"Skipping {url} (already downloaded)")
            return

        try:
            print(f"Downloading file from {url}")
            # Send HTTP GET request to download the file
            if TOKEN == "Replace your token":
                response = requests.get(url, headers={
                                        'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            else:
                response = requests.get(url, headers=HEADERS, timeout=30)
            # Handle 429 too many request error
            if response.status_code == 429:
                print("Too many requests, waiting for 60 seconds")
                time.sleep(int(response.headers["Retry-After"]))
            response.raise_for_status()  # Raise an exception for HTTP errors
            # Extract filename from URL
            filename = os.path.basename(url)
            # Add tags to each filename
            # Separate tags with "_"
            filename = tags_dict['Category'] + "_" + tags_dict['Subcategory'] + \
                "_" + tags_dict['Project_name'] + "_" + filename
            # If the file is in English, download it
            if isFileEnglish(response.content):
                # Write downloaded content to file
                with open(os.path.join(output_directory, filename), 'wb') as f:
                    f.write(response.content)
            # Update cache immediately
            cache.add(url)
            save_cache(url)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download file from {url}: {e}")
        except Exception as e:
            print(f"Unexpected error while downloading file from {url}: {e}")


def downloader_multi_thread(download_urls, output_directory, tags_dict, cache):
    """
    Downloads the files from the URLs provided in the input download_urls in the output_directory. Also, tags each downloaded file with
    corresponding Category, Subcategory, and Project_name in each file name. It accomplishes this task in a multi-thread manner and downloads 
    multiple files at the same time.
    Args:
        download_urls (dict): A dictionary which contains a list of URLs for each file extension.
        output_directory (str): The path where the downloaded files will be stored.
        tags_dict(dict): A dictionary containing the tags for each file. For example: Category, Subcategory, Project_name

    """
    # Calculate a reasonable max_threads based on system capabilities
    max_threads = multiprocessing.cpu_count() * 2  # Example: twice the number of CPU cores
    for file_format in download_urls:
        # Exclude yml and yaml files from downloading
        if file_format in ["yml", "yaml"]:
            continue
        urls_list = download_urls[file_format]
        semaphore = threading.Semaphore(max_threads)
        threads = []
        for url in urls_list:
            thread = threading.Thread(target=downloader, args=(
                url, output_directory, tags_dict, semaphore, cache))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()


def download_files_from_yaml(yaml_file="../../sources/landscape_augmented_repos_websites.yml", output_directory="sources/raw_files"):
    """
    Downloads the files with specific extensions from the URLs provided in yaml_file

    Args:
        yaml_file (str, optional): The path to the URLs yaml file (default: sources/landscape_augmented.yml).
        output_directory (str, optional): The path where the downloaded files will be stored (default: sources/raw_files).

    """
    # Load URLs from YAML file
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Load cache
    cache = load_cache()

    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {'Category': "", 'Subcategory': "", 'Project_name': ""}
    # Process the loaded data
    for category in data['landscape']:
        # It downloads only below-defined categories to avoid duplication
        category_list = ["App Definition and Development", "Orchestration & Management", "Runtime",
                         "Provisioning", "Observability and Analysis", "Test_Provisioning"]
        if category['name'] not in category_list:
            continue
        tags_dict['Category'] = category['name']
        print(f"Category: {tags_dict['Category']}")
        for subcategory in category.get('subcategories', []):
            tags_dict['Subcategory'] = subcategory['name']
            print(f"Subcategory: {tags_dict['Subcategory']}")
            for item in subcategory.get('items', []):
                tags_dict['Project_name'] = item['name']
                print(f"Item: {tags_dict['Project_name']}")
                repo = item.get('repo', {})
                downloader_multi_thread(
                    repo.get('download_urls', []), output_directory, tags_dict, cache)
        # Adding all the files corresponding to a category to a zip file
        shutil.make_archive(
            "sources/" + tags_dict['Category'], 'zip', output_directory+"/")
        # Removing remaining raw files after archiving
        # shutil.rmtree(output_directory)
        # Create directory for the next category
        os.makedirs(output_directory, exist_ok=True)


# Example usage:
if __name__ == "__main__":
    download_files_from_yaml()
