import os
import json
import yaml
from tqdm import tqdm
import PyPDF2
from datetime import datetime
import logging

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
    subcategory= parts[1]
    project_name = parts[2]
    filename = '_'.join(parts[3:])
    
    return {
        "category": category,
        "subcategory": subcategory,
        "project_name": project_name,
        "file_name": filename,
    }


def convert_files_to_json(processed_files, chunk_size, error_file_list, json_file_path = "sources/unified_files", file_paths = "sources/raw_files"):
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
    def convert_datetime_to_str(data):
        if isinstance(data, dict):
            return {key: convert_datetime_to_str(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [convert_datetime_to_str(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
    for file_name in tqdm(files):

        if file_name in processed_files:
            # print(f"Skipping already processed file: {file_name}")
            continue
        if file_name.lower().endswith(".yaml") or file_name.lower().endswith(".yml"):
            try:
                with open(os.path.join(file_paths, file_name), "r", encoding="utf-8") as yaml_file:
                    documents = yaml.safe_load_all(yaml_file)
                    for data in documents:
                        cleaned_data = convert_datetime_to_str(data)
                        tag_data = extract_metadata(file_name)

                        yaml_data = {"tag": tag_data, "content": cleaned_data}

                        # Add the YAML data to the list
                        yaml_data_list.append(yaml_data)

            except yaml.YAMLError as exc:
                # print(f"Error writing YAML data to JSON file: {exc}: {file_name}")
                error_file_list.append(file_name)
                processed_files.add(file_name)
                processed_urls_count += 1
                continue
            # Write the list of YAML data to the JSON file
            try:
                with open(os.path.join(json_file_path, "yaml_data.json"), "w", encoding='utf-8') as json_file:
                    json.dump(yaml_data_list, json_file, indent=4, default=str)
                
            except Exception as e:
                logging.error(f"Error writing YAML data to JSON file: {e}: {file_name}")
                error_file_list.append(file_name)
                continue
            processed_files.add(file_name)  # Add the processed file to the set
            processed_urls_count += 1

        elif file_name.lower().endswith(".md"):
            data = []
            current_heading = ""
            current_content = ""
            extra_info = ""
            not_impo_content = ""
            inside_code_block = False

            try:
                with open(os.path.join(file_paths, file_name), "r", encoding="utf-8") as md_file:
                    md_content = md_file.read()

                lines = md_content.split("\n")

                for line in lines:
                    if line == "":
                        continue
                    if (line.startswith("*") and line.endswith("*")) or line.startswith("#"):
                        if current_heading:
                            data.append(
                                {
                                    "heading": current_heading.strip(),
                                    "data": current_content.strip(),
                                }
                            )

                        current_heading = line.strip("*#").strip()
                        current_content = ""
                        extra_info = ""
                    else:
                        if line.startswith("```") or line.startswith("```"):
                            inside_code_block = not inside_code_block
                        elif not inside_code_block:
                            current_content += line.strip() + "\n "
                        else:
                            if line.strip() not in current_content:
                                extra_info += line.strip() + "\n "  
                        if not (
                            line.startswith("*") and line.endswith("*")
                        ) and not line.startswith("#"):
                            not_impo_content += line.strip() + "\n "

                if current_heading:
                    current_content = current_content.replace("\n", " ")
                    current_heading = current_heading.replace("\n", " ")

                    data.append(
                        {
                            "heading": current_heading.strip(),
                            "data": current_content.strip(),
                        }
                    )

                    not_impo_content = not_impo_content.replace(current_content, " ")
                    not_impo_content = not_impo_content.replace(current_heading, "")

                if not_impo_content:
                    data.append({"additional_info": not_impo_content.strip().replace("\n", " ")})

                tag_data = extract_metadata(file_name)

                json_data = {
                    "tag": tag_data,
                    "content": data
                }

                md_data_list.append(json_data)
                
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")
                error_file_list.append(file_name)

            with open(os.path.join(json_file_path, "md_data.json"), "w", encoding="utf-8") as json_file:
                json.dump(md_data_list, json_file, indent=4)
            processed_files.add(file_name) 
            processed_urls_count += 1
            
        
        else:        
            try:
                        content = ''                                 
                        with open(os.path.join(file_paths, file_name), 'rb') as file:
                            reader = PyPDF2.PdfReader(file)
                            for page in reader.pages:
                                content += page.extract_text()

                            tag_data = extract_metadata(file_name)
                            yaml_data = {"tag": tag_data, "content": content}
                            pdf_data_list.append(yaml_data)
                    
                        with open(os.path.join(json_file_path, "pdf_data.json"), 'w', encoding='utf-8') as json_file:
                            json.dump(pdf_data_list, json_file, indent=4)
                        processed_files.add(file_name)
                        processed_urls_count += 1
                        
            except Exception as e:
                    print(f"Error converting PDF to JSON: {e}")
                    error_file_list.append(file_name)

        if processed_urls_count >= total_chunk_size:
                # print("Chunk size reached. Stopping processing.")
                return 

def process_error_yaml_file(error_file_list: list, file_paths = "sources/raw_files", json_file_path = "sources/unified_files" ) -> None:
    """Processes error YAML files and stores them in JSON format.
     Some of the YAML files contain special symbols and are not formatted correctly. As a result, these files cannot be loaded properly. Therefore, the problematic files are appended 
     to the list, and their data is converted into strings and stored in the 'content' key.

    Args:
        error_file_list (list): List of error file names.
    """
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
