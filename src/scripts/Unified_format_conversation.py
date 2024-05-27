import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import json
import yaml
from tqdm import tqdm
import PyPDF2
from datetime import datetime
import logging

# Constants for processing
MIN_NUMBER_OF_TOKENS = 50  # Example value, adjust as needed
NUMBER_OF_TOKENS = 600  # Example value, adjust as needed

def convert_datetime_to_str(data):
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
        error_file (str): The name of the file.
        file name is usee as Tag from where data is coming from

    Returns:
        dict: A dictionary containing metadata information.
    """
    parts = file_name.split('_')

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

def convert_files_to_json(processed_files, chunk_size, error_file_list, json_file_path="sources/unified_files", file_paths="sources/raw_files"):
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

    files = os.listdir(file_paths)
    yaml_data_list = []
    md_data_list = []
    pdf_data_list = []
    processed_urls_count = len(processed_files)
    total_chunk_size = chunk_size + processed_urls_count

    def process_file(file_name):
        nonlocal processed_urls_count

        if file_name in processed_files:
            return None

        file_path = os.path.join(file_paths, file_name)
        lower_file_name = file_name.lower()

        if lower_file_name.endswith((".yaml", ".yml")):
            try:
                with open(file_path, "r", encoding="utf-8") as yaml_file:
                    documents = yaml.safe_load_all(yaml_file)
                    for data in documents:
                        cleaned_data = convert_datetime_to_str(data)
                        tag_data = extract_metadata(file_name)
                        yaml_data_list.append({"tag": tag_data, "content": cleaned_data})
                processed_files.add(file_name)
                processed_urls_count += 1
                return "yaml"
            except yaml.YAMLError as exc:
                logging.error(f"Error processing YAML file: {exc}: {file_name}")
                error_file_list.append(file_name)
                processed_files.add(file_name)
                processed_urls_count += 1
                return None

        elif lower_file_name.endswith(".md"):
            try:
                with open(file_path, "r", encoding="utf-8") as md_file:
                    md_content = md_file.read()

                md_content = re.sub(r'[^\x00-\x7F]+', '', md_content)
                md_content = remove_links_from_markdown(md_content)
                md_content = clean_markdown(md_content)
                words = md_content.split()

                if len(words) <= MIN_NUMBER_OF_TOKENS:
                    processed_files.add(file_name)
                    processed_urls_count += 1
                    print(f"File has less than {MIN_NUMBER_OF_TOKENS} words, skipping file")
                    return None

                data = []
                start_index = 0
                old_index = 0

                for index, word in enumerate(words):
                    if '#' in word:
                        if index - start_index < NUMBER_OF_TOKENS + 1:
                            old_index = index
                        else:
                            if old_index - start_index > MIN_NUMBER_OF_TOKENS:
                                chunk = ' '.join(words[start_index:old_index - 1])
                                data.append({"data": chunk})
                                start_index = old_index

                if NUMBER_OF_TOKENS >= len(words) - start_index >= MIN_NUMBER_OF_TOKENS:
                    chunk = ' '.join(words[start_index:])
                    data.append({"data": chunk})
                elif len(words) - start_index > NUMBER_OF_TOKENS:
                    chunk = ' '.join(words[start_index:start_index + NUMBER_OF_TOKENS])
                    data.append({"data": chunk})

                tag_data = extract_metadata(file_name)
                md_data_list.append({"tag": tag_data, "content": data})
                processed_files.add(file_name)
                processed_urls_count += 1
                return "md"
            except Exception as e:
                logging.error(f"Error processing Markdown file: {e}: {file_name}")
                error_file_list.append(file_name)
                return None

        elif lower_file_name.endswith(".pdf"):
            try:
                content = ''
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        content += page.extract_text()

                tag_data = extract_metadata(file_name)
                pdf_data_list.append({"tag": tag_data, "content": content})
                processed_files.add(file_name)
                processed_urls_count += 1
                return "pdf"
            except Exception as e:
                logging.error(f"Error converting PDF to JSON: {e}: {file_name}")
                error_file_list.append(file_name)
                return None

        return None

    def write_json_data():
        try:
            with open(os.path.join(json_file_path, "yaml_data.json"), "a", encoding='utf-8') as json_file:
                json.dump(yaml_data_list, json_file, indent=4, default=str)
                json_file.write('\n')
            with open(os.path.join(json_file_path, "md_data.json"), "a", encoding='utf-8') as json_file:
                json.dump(md_data_list, json_file, indent=4)
                json_file.write('\n')
            with open(os.path.join(json_file_path, "pdf_data.json"), "a", encoding='utf-8') as json_file:
                json.dump(pdf_data_list, json_file, indent=4)
                json_file.write('\n')
        except Exception as e:
            logging.error(f"Error writing JSON data: {e}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_file, file_name): file_name for file_name in files}
        for future in tqdm(as_completed(futures)):
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
    reference_definition_pattern = re.compile(r'^\s*\[.*?\]:\s*.*', re.MULTILINE)

    # Remove inline links
    content = inline_link_pattern.sub('', content)

    # Remove reference-style links
    content = reference_link_pattern.sub('', content)

    # Remove reference link definitions
    content = reference_definition_pattern.sub('', content)

    return content


def process_error_yaml_file(error_file_list: list, file_paths="sources/raw_files",
                            json_file_path="sources/unified_files") -> None:
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
            with open(os.path.join(file_paths, error_file), "r", encoding="utf-8") as yaml_file:
                documents = yaml_file.read()
                tag_data = extract_metadata(error_file)
                yaml_data = {"tag": tag_data, "content": documents}
                yaml_data_list.append(yaml_data)
        except Exception as e:
            logging.error(f"An error occurred while processing {error_file}: {e}")
    try:
        with open(os.path.join(json_file_path, "error_yaml_data.json"), "w", encoding='utf-8') as json_file:
            json.dump(yaml_data_list, json_file, indent=4)
    except Exception as e:
        logging.error(f"An error occurred while writing JSON file: {e}")


def clean_markdown(markdown_text):
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
    markdown_text = re.sub(r'^\s*[-*+]\s+', '', markdown_text, flags=re.MULTILINE)
    # Remove ordered list markers
    markdown_text = re.sub(r'^\s*\d+\.\s+', '', markdown_text, flags=re.MULTILINE)
    # Remove extra spaces and newlines
    markdown_text = re.sub(r'\s+', ' ', markdown_text).strip()
    return markdown_text


processed_files_record = 'sources/processed_files.txt'
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
