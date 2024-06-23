# This script processes various file types (YAML, Markdown, and PDF) from a specified directory,
# converts them into JSON format, and stores the JSON files in a designated directory. 

# Key Features:
# 1. Extracts metadata from file names.
# 2. Converts files to JSON format, handling YAML, Markdown, and PDF files.
# 3. Removes links and cleans Markdown content.
# 4. Logs errors encountered during processing.
# 5. Handles problematic YAML files by storing their raw content.

# The script uses several helper functions to ensure clean data and efficient processing. Processed files are tracked to avoid reprocessing in subsequent runs.

# Modules:
# - os, re, json, yaml, tqdm, PyPDF2, datetime, logging

# Constants:
# - NUMBER_OF_TOKENS: The number of tokens used to split Markdown content.
# - MIN_NUMBER_OF_TOKENS: The minimum number of tokens required for a Markdown chunk.

# Functions:
# - extract_metadata(file_name: str) -> dict: Extracts and returns metadata from the file name.
# - convert_files_to_json(processed_files, chunk_size, error_file_list, json_file_path="sources/unified_files", file_paths="sources/raw_files"): Converts files in the specified directory to JSON format.
# - remove_links_from_markdown(content: str) -> str: Removes all markdown links from the provided content.
# - process_error_yaml_file(error_file_list: list, file_paths="sources/raw_files", json_file_path="sources/unified_files") -> None: Processes YAML files that encountered errors and stores their raw content in JSON format.
# - clean_markdown(markdown_text): Cleans the markdown content by removing headers, emphasis, links, images, and other formatting.

# Execution:
# - Initializes the set of processed files from a record file if it exists.
# - Calls convert_files_to_json to process files.
# - Calls process_error_yaml_file to handle error files.
# - Updates the record of processed files.


import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import json
import yaml
import PyPDF2
from datetime import datetime
import logging
from threading import Lock
import multiprocessing
from typing import Any, List, Set
# Constants for processing
MIN_NUMBER_OF_TOKENS = 50  # Example value, adjust as needed
NUMBER_OF_TOKENS = 600  # Example value, adjust as needed

def convert_datetime_to_str(data: Any) -> Any:
    if isinstance(data, dict):
       return {key: convert_datetime_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_datetime_to_str(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

def extract_metadata(file_name: str) -> dict:
    """Extracts metadata from the file name.

    Args:
        file_name (str): The full path of the file.
        file name is used as Tag from where data is coming from

    Returns:
        dict: A dictionary containing metadata information.
    """
    # Extract the file name from the path
    file_name_only = os.path.basename(file_name)

    parts = file_name_only.split('_')

    # Extract category, subcategory, project name, and filename
    category = parts[0]
    subcategory = parts[1]
    project_name = parts[2]
    filename = '_'.join(parts[3:])

    return {
        "category": category,
        "subcategory": subcategory,
        "project_name": project_name,
        "file_name": filename,
    }

def convert_files_to_json(processed_files: Set[str], chunk_size: int, error_file_list: List[str], json_file_path: str = "sources/unified_files", file_paths: str = "sources/raw_files") -> None:
    """Converts various file types to JSON.

    Args:
        file_paths (str): Path to the directory containing files.
        json_file_path (str): Path to the directory to store JSON files.
        processed_files (set): Set of processed file names.
        chunk_size (int): Size of processing chunk.
        error_file_list (list): List to store error file names.
    """
    if not os.path.exists(file_paths):
        os.makedirs(file_paths)
    if not os.path.exists(json_file_path):
        os.makedirs(json_file_path)
    yaml_lock = Lock()
    md_lock = Lock()
    pdf_lock = Lock()
    error_lock = Lock()
    processed_files_lock = Lock()
    yaml_data_list = []
    md_data_list = []
    pdf_data_list = []
    processed_urls_count = len(processed_files)
    file_names = glob.glob(file_paths + "/*/*.*", recursive=True)
    file_names = file_names + glob.glob(file_paths + "/*.*")

    def process_file(file_name):
        nonlocal processed_urls_count

        if file_name in processed_files:
            return None

        lower_file_name = file_name.lower()

        if lower_file_name.endswith((".yaml", ".yml")):
            data = []
            try:
                with open(file_name, "r", encoding="utf-8") as yaml_file:
                    documents = yaml.safe_load_all(yaml_file)
                    for doc in documents:
                        cleaned_data = convert_datetime_to_str(doc)
                        data.append({'data': cleaned_data})
                    tag_data = extract_metadata(file_name.split('/')[-1])
                with yaml_lock:
                    yaml_data_list.append({"tag": tag_data, "content": data})
                with processed_files_lock:
                    processed_files.add(file_name)
                processed_urls_count += 1
                return "yaml"
            except yaml.YAMLError as exc:
                logging.error(f"Error processing YAML file: {exc}: {file_name}")
                with error_lock:
                    error_file_list.append(file_name)
                with processed_files_lock:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                return None

        elif lower_file_name.endswith(".md"):
            try:
                with open(file_name, "r", encoding="utf-8") as md_file:
                    md_content = md_file.read()

                md_content = re.sub(r'[^\x00-\x7F]+', '', md_content)
                md_content = remove_links_from_markdown(md_content)
                md_content = clean_markdown(md_content)
                words = md_content.split()
                file_length = len(words)

                if file_length <= MIN_NUMBER_OF_TOKENS:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                    print(f"File has less than {MIN_NUMBER_OF_TOKENS} words, skipping file")
                    return None

                splits = int(file_length / NUMBER_OF_TOKENS + 1)
                split_length = int(file_length / splits)
                data = []
                start_index = 0
                end_index = 0

                for i in range(1, splits):
                    for j in range(split_length):
                        if "#" in words[split_length * i - j]:
                            end_index = split_length * i-j-1
                            break
                        if "." in words[split_length * i - j]:
                            end_index = split_length * i - j
                            break
                    chunk = ' '.join(words[start_index:end_index])
                    data.append({"data": chunk})
                    start_index = end_index + 1

                chunk = ' '.join(words[start_index:start_index + NUMBER_OF_TOKENS])
                data.append({"data": chunk})

                tag_data = extract_metadata(file_name.split('/')[-1])
                with md_lock:
                    md_data_list.append({"tag": tag_data, "content": data})
                with processed_files_lock:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                return "md"
            except Exception as e:
                logging.error(f"Error processing Markdown file: {e}: {file_name}")
                with error_lock:
                    error_file_list.append(file_name)
                with processed_files_lock:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                return None

        elif lower_file_name.endswith(".pdf"):
            data = []
            try:
                content = ''
                with open(file_name, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        content += page.extract_text()
                data.append({'data': content})
                tag_data = extract_metadata(file_name.split('/')[-1])
                if not content == "":
                    with pdf_lock:
                        pdf_data_list.append({"tag": tag_data, "content": data})
                with processed_files_lock:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                return "pdf"
            except Exception as e:
                logging.error(f"Error converting PDF to JSON: {e}: {file_name}")
                with error_lock:
                    error_file_list.append(file_name)
                with processed_files_lock:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                return None

        return None

    def write_json_data() -> None:
        try:
            if yaml_data_list:
                with open(os.path.join(json_file_path, "yaml_data.json"), "a", encoding='utf-8') as json_file:
                    json.dump(yaml_data_list, json_file, indent=4, default=str)
                    json_file.write('\n')
            if md_data_list:
                with open(os.path.join(json_file_path, "md_data.json"), "a", encoding='utf-8') as json_file:
                    json.dump(md_data_list, json_file, indent=4)
                    json_file.write('\n')
            if pdf_data_list:
                with open(os.path.join(json_file_path, "pdf_data.json"), "a", encoding='utf-8') as json_file:
                    json.dump(pdf_data_list, json_file, indent=4)
                    json_file.write('\n')
        except Exception as e:
            logging.error(f"Error writing JSON data: {e}")
    max_workers = multiprocessing.cpu_count() * 2
    with ThreadPoolExecutor(max_workers) as executor:
        futures = {executor.submit(process_file, file_name): file_name for file_name in file_names}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    # Periodically write to JSON files
                    if processed_urls_count % chunk_size == 0:
                        write_json_data()
                        yaml_data_list.clear()
                        md_data_list.clear()
                        pdf_data_list.clear()
            except Exception as exc:
                logging.error(f'File generated an exception: {exc}')

    # Write any remaining data to JSON files
    write_json_data()

def remove_links_from_markdown(content: str) -> str:
    """
    Remove all markdown links from the provided markdown content.

    Args:
    - content (str): The markdown content as a string.

    Returns:
    - str: The markdown content with all links removed.
    """
    # Regex pattern to match inline markdown links [text](url) and ![image](url)
    inline_link_pattern = re.compile(r'!?\[.*?\]\(.*?\)')

    # Regex pattern to match reference-style markdown links [text][id]
    reference_link_pattern = re.compile(r'\[.*?\]\[.*?\]')

    # Regex pattern to match reference link definitions [id]: url "title"
    reference_definition_pattern = re.compile(
        r'^\s*\[.*?\]:\s*.*', re.MULTILINE)

    # Remove inline links
    content = inline_link_pattern.sub('', content)

    # Remove reference-style links
    content = reference_link_pattern.sub('', content)

    # Remove reference link definitions
    content = reference_definition_pattern.sub('', content)

    return content


def process_error_yaml_file(error_file_list: List[str], file_paths: str = "sources/raw_files", json_file_path: str = "sources/unified_files") -> None:
    """Processes error YAML files and stores them in JSON format.
     Some of the YAML files contain special symbols and are not formatted correctly. As a result, these files cannot be loaded properly. Therefore, the problematic files are appended 
     to the list, and their data is converted into strings and stored in the 'content' key.

    Args:
        error_file_list (list): List of error file names.
    """
    # Return early if error_file_list is empty
    if not error_file_list:
        return
    yaml_data_list = []
    for error_file in error_file_list:
        try:
            with open(error_file, "r", encoding="utf-8") as yaml_file:
                documents = yaml_file.read()
                tag_data = extract_metadata(error_file)
                yaml_data = {"tag": tag_data, "content": documents}
                yaml_data_list.append(yaml_data)
        except Exception as e:
            logging.error(
                f"An error occurred while processing {error_file}: {e}")
    try:
        with open(os.path.join(json_file_path, "error_yaml_data.json"), "w", encoding='utf-8') as json_file:
            json.dump(yaml_data_list, json_file, indent=4)
    except Exception as e:
        logging.error(f"An error occurred while writing JSON file: {e}")


def clean_markdown(markdown_text: str) -> str:
    # Remove Markdown headers (lines starting with #)
    markdown_text = re.sub(r'^\s*#.*$', '', markdown_text, flags=re.MULTILINE)
    # Remove emphasis (bold and italics)
    markdown_text = re.sub(r'(\*{1,2}|_{1,2})(.*?)\1', r'\2', markdown_text)
    # Remove strikethrough
    markdown_text = re.sub(r'~~(.*?)~~', r'\1', markdown_text)
    # Remove inline code
    # markdown_text = re.sub(r'`(.*?)`', r'\1', markdown_text)
    # Remove code blocks
    # markdown_text = re.sub(r'```.*?```', '', markdown_text, flags=re.DOTALL)
    # Remove blockquotes
    markdown_text = re.sub(r'^>\s?', '', markdown_text, flags=re.MULTILINE)
    # Remove links but keep the text
    # markdown_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', markdown_text)
    # Remove images
    markdown_text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', markdown_text)
    # Remove horizontal rules
    markdown_text = re.sub(r'---', '', markdown_text)
    # Remove unordered list markers
    markdown_text = re.sub(r'^\s*[-*+]\s+', '',
                           markdown_text, flags=re.MULTILINE)
    # Remove ordered list markers
    markdown_text = re.sub(r'^\s*\d+\.\s+', '',
                           markdown_text, flags=re.MULTILINE)
    # Remove extra spaces and newlines
    markdown_text = re.sub(r'\s+', ' ', markdown_text).strip()
    return markdown_text


processed_files_record = 'sources/unified_processed_files.txt'
processed_files = set()
if os.path.exists(processed_files_record):
    with open(processed_files_record, 'r', encoding='utf-8') as f:
        processed_files = set(f.read().splitlines())
chunk_size = 80000
error_file_list = []

# file_paths = "sources/raw_files"
# json_file_path = "sources/unified_files"
# Create output directory if it doesn't exist
# os.makedirs(exist_ok=True)
convert_files_to_json(processed_files, chunk_size, error_file_list)
process_error_yaml_file(error_file_list)

with open(processed_files_record, 'w', encoding='utf-8') as f:
    for file_url in processed_files:
        f.write(file_url + '\n')
