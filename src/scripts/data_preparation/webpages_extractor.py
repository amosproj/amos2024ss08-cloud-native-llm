"""
This script downloads text content from web pages and Google Docs URLs specified in a YAML file. It utilizes 
multithreading for concurrent downloads and manages caching to avoid redundant downloads.

Dependencies:
- yaml
- os
- shutil
- requests
- BeautifulSoup
- pandas
- threading
- re
- multiprocessing

Functions:
- `load_cache()`: Loads URLs from a cache file to skip redundant downloads.
- `save_cache(url)`: Saves a URL to the cache file after downloading its content.
- `save_doc_to_pdf(url, output_directory, tags)`: Downloads a Google Doc as a PDF and saves it.
- `save_strings_to_md(string, output_dir, tags)`: Saves extracted text content to a Markdown file.
- `downloader(url, output_directory, tags, semaphore, cache)`: Handles downloading content from URLs.
- `extract_text(links, output_directory, tags, cache)`: Manages multithreaded extraction of text content.
- `download_files_from_yaml(yaml_file, output_directory)`: Downloads content from URLs specified in a YAML file.

Usage:
- Specify the YAML file containing URLs and the output directory for downloaded files.
- Run the script to download text content from web pages and Google Docs, organizing files by category and subcategory.
"""

import yaml
import os
import shutil
import requests
from bs4 import BeautifulSoup
import pandas as pd
import threading
import re
import multiprocessing
from typing import Any

CACHE_FILE = 'webpages_extractor_cache.txt'


def load_cache() -> set[str]:
    """
    Load the cache from the cache file.

    Returns:
        Set[str]: A set containing cached items as strings.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()


def save_cache(url: str) -> None:
    """
    Save the cache to the cache file.

    Args:
        url (str): The URL to be saved in the cache file.

    Returns:
        None
    """
    with open(CACHE_FILE, 'a') as f:
        f.write(url + '\n')

def save_doc_to_pdf(url: str, output_directory: str, tags: dict[str, str]) -> None:
    """
    Save a Google Document as PDF.

    Args:
        url (str): The URL of the Google Document.
        output_directory (str): The directory where the PDF file will be saved.
        tags (Dict[str, str]): A dictionary containing tags such as 'Category', 'Subcategory', 'Project_name',
                                and 'filename' to construct the PDF file name.

    Returns:
        None
    """

    export_url = "https://docs.google.com/document/export?format={}&id={}".format('pdf', url.split('/')[-2])
    # Send GET request to export URL
    response = requests.get(export_url)
    filename = os.path.join(
        output_directory,
        tags["Category"]
        + "_"
        + tags["Subcategory"]
        + "_"
        + tags["Project_name"]
        + "_"
        + tags["filename"]
        + ".pdf",
    )
    # Write the response content (PDF data) to a file
    with open(filename, 'wb') as f:
        f.write(response.content)

def save_strings_to_md(string: str, output_dir: str, tags: dict[str, str]) -> None:
    """
    Save a string to a Markdown (.md) file.

    Args:
        string (str): The string content to be saved.
        output_dir (str): The directory where the Markdown file will be saved.
        tags (Dict[str, str]): A dictionary containing tags such as 'Category', 'Subcategory', 'Project_name',
                                and 'filename' to construct the Markdown file name.

    Returns:
        None
    """

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = os.path.join(
        output_dir,
        tags["Category"]
        + "_"
        + tags["Subcategory"]
        + "_"
        + tags["Project_name"]
        + "_"
        + tags["filename"]
        + ".md",
    )
    # Write the content to the file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(string)
        
def downloader(url: str, output_directory: str, tags: dict[str, str], semaphore: Any, cache: set) -> None:
    """
    Download content from a URL and save it based on its type.

    Args:
        url (str): The URL of the content to download.
        output_directory (str): The directory where downloaded files will be saved.
        tags (Dict[str, str]): A dictionary containing tags such as 'Category', 'Subcategory', 'Project_name',
                                and 'filename' to categorize and name downloaded files.
        semaphore (Any): A synchronization primitive to control concurrent access.
        cache (set): A set containing cached URLs to avoid redundant downloads.

    Returns:
        None
    """
    
    with semaphore:
        if url in cache:
            print(f"Skipping {url} (already downloaded)")
            return
        try:
            # check if it is a link to google doc
            if url.startswith("https://docs.google.com/document/"):
                # download the google doc in pdf format
                save_doc_to_pdf(url, output_directory, tags)
                # Update cache immediately
                cache.add(url)
                save_cache(url)
                # dont continue with further scraping
                return None
                
            # Send a GET request to the webpage
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            temp = ""
            # Remove any characters that are invalid in filenames
            filename = os.path.basename(url)
            # Remove any characters that are invalid in filenames
            tags["filename"] = re.sub(r'[<>:"/\\|?*]', '_', filename)
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the content of the response with BeautifulSoup
                soup = BeautifulSoup(response.content, "lxml")

                body = soup.body
                if body:
                    for element in body.descendants:
                        if element.name == "p":
                            temp += element.get_text()
                            temp += "\n"
                        elif element.name == "pre":
                            temp += "```\n" + element.get_text() + "```"
                            temp += "\n"
                        elif element.name == "table":
                            df = pd.read_html(str(element))[0]
                            temp += df.to_markdown(index=False)
                            temp += "\n"

                    # print(temp)
                    save_strings_to_md(temp, output_directory, tags)
                    # Update cache immediately
                    cache.add(url)
                    save_cache(url)
            else:
                print(
                    f"Failed to retrieve the webpage. Status code: {response.status_code}"
                )
        except Exception as e:
            print(f"Failed to retrieve the webpage: {url}. Error: {e}")

def extract_text(links: list[str], output_directory: str, tags: dict[str, str], cache: set) -> None:
    """
    Extract text content from a list of URLs concurrently.

    Args:
        links (List[str]): List of URLs from which to extract text content.
        output_directory (str): The directory where downloaded files will be saved.
        tags (Dict[str, str]): A dictionary containing tags such as 'Category', 'Subcategory', 'Project_name',
                                and 'filename' to categorize and name downloaded files.
        cache (set): A set containing cached URLs to avoid redundant downloads.

    Returns:
        None
    """
    
    max_threads = multiprocessing.cpu_count() * 2  # Example: double the number of cores
    semaphore = threading.Semaphore(max_threads)
    threads = []
    for url in links:
        thread = threading.Thread(target=downloader, args=(
            url, output_directory, tags, semaphore, cache))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    


def download_files_from_yaml(
    yaml_file: str = "../../../sources/landscape_augmented_repos_websites.yml",
    output_directory: str = "sources/raw_files"
) -> None:
    """
    Downloads the files with specific extensions from the URLs provided in yaml_file.

    Args:
        yaml_file (str, optional): The path to the URLs yaml file (default: sources/landscape_augmented.yml).
        output_directory (str, optional): The path where the downloaded files will be stored (default: sources/raw_files).

    Returns:
        None
    """

    # Load URLs from YAML file
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Load cache
    cache = load_cache()
    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {"Category": "", "Subcategory": "", "Project_name": "", "filename": ""}
    # Process the loaded data
    for category in data["landscape"]:
        # It downloads only below defined categories to avoid duplication
        category_list = [
            "App Definition and Development",
            "Orchestration & Management",
            "Runtime",
            "Provisioning",
            "Observability and Analysis",
            "Test_Provisioning",
        ]
        if category["name"] not in category_list:
            continue
        tags_dict["Category"] = category["name"]
        print(f"Category: {tags_dict['Category']}")
        for subcategory in category.get("subcategories", []):
            tags_dict["Subcategory"] = subcategory["name"]
            print(f"Subcategory: {tags_dict['Subcategory']}")
            for item in subcategory.get("items", []):
                tags_dict["Project_name"] = item["name"]
                print(f"Item: {tags_dict['Project_name']}")
                website = item.get("website", {})
                extract_text(website.get("docs", []), output_directory, tags_dict, cache)
                
    # Adding all the files corresponding to a category to a zip file
    shutil.make_archive(
        "sources/" + "webpages_documentations", "zip", output_directory + "/"
    )
    # Removing remminig raw files after archiving
    # shutil.rmtree(output_directory)
    # Creat dirrectory for next category
    #os.makedirs(output_directory, exist_ok=True)


# Example usage:
if __name__ == "__main__":
    download_files_from_yaml()
