import requests
import yaml
import os
from tqdm import tqdm
import threading
import shutil


TOKEN = "Replace your token"  # Replace with your GitHub token to increas github API hourly rate to 5000
HEADERS = {'Authorization': f'Bearer {TOKEN}'}
def downloader(url, output_directory, tags_dict, semaphore):
    """
    This function downloads a single file from the url in the input. It is used by downloader_multi_thread() at each thread. 
    This function uses a semaphore to control the number of concurrent downloads.
    Args:
        url (str): A single url string.
        output_directory (str): The path where the downloaded files will be stored.
        tags_dict(dict): A dictionary containing the tags for each file. For example: Category, Subcategory, Project_name
        semaphore (threading.Semaphore): A semaphore object used to limit the number of concurrent downloads.
    """
    with semaphore:
        try:
            # Send HTTP GET request to download the file
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # Raise an exception for HTTP errors
            # Extract filename from URL
            filename = os.path.basename(url)
            # Add tags to each filename
            # Seperate tags with "_"
            filename = tags_dict['Category'] +"_"+ tags_dict['Subcategory'] +"_"+ tags_dict['Project_name'] +"_"+ filename

            # Write downloaded content to file
            with open(os.path.join(output_directory, filename), 'wb') as f:
                f.write(response.content)

        except Exception as e:
            print(f"Failed to download file from {url}: {e}")
                
def downloader_multi_thread(download_urls, output_directory, tags_dict):
    """
    Downloads the files from the URLs provided in the input download_urls in the output_directory. Also, tags each downloaded file with
    corresponding  Category, Subcategory and Project_name in each file name. It accomplishes this task in a multi thread manner and downloads 
    multiple files at the same time.
    Args:
        download_urls (dict): A dictionary which contains a list of URLs for each file extention.
        output_directory (str): The path where the downloaded files will be stored.
        tags_dict(dict): A dictionary containing the tags for each file. For example: Category, Subcategory, Project_name
        
    """
    max_threads = 16
    for file_format in download_urls:
        # exclude yml and yaml files from downloading
        if file_format in ["yml","yaml"]:
            continue
        urls_list = download_urls[file_format]
        semaphore = threading.Semaphore(max_threads)
        threads = []
        for url in urls_list:
            thread = threading.Thread(target=downloader, args=(url, output_directory, tags_dict, semaphore))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        
    
def download_files_from_yaml(yaml_file = "sources/landscape_augmented.yml", output_directory = "sources/raw_files"):
    """
    Downloads the files with specific extensions from the URLs provided in yaml_file

    Args:
        yaml_file (str, optional): The path to the URLs yaml file(default: sources/landscape_augmented.yml).
        output_directory (str, optional): The path where the downloaded files will be stored(defult: sources/raw_files).
        
    """
    # Load URLs from YAML file
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {'Category': "", 'Subcategory': "", 'Project_name': ""}
    # Process the loaded data 
    for category in data['landscape']:
    # Use below block if already downloaded a category and you don't want to downloaded it again. 
    #    if category['name'] == "Provisioning":
    #        continue
        tags_dict['Category'] = category['name']
        print(f"Category: {tags_dict['Category']}")
        for subcategory in category.get('subcategories', []):
            tags_dict['Subcategory'] = subcategory['name']
            print(f"Subcategory: {tags_dict['Subcategory']}")
            for item in tqdm(subcategory.get('items', [])):
                tags_dict['Project_name'] = item['name']
                print(f"Item: {tags_dict['Project_name']}")
                downloader_multi_thread(item.get('download_urls',[]),output_directory, tags_dict)
        # Adding all the files corresponding to a category to a zip file
        shutil.make_archive("sources/"+ tags_dict['Category'], 'zip', output_directory+"/")
        # Removing remminig raw files after archiving
        shutil.rmtree(output_directory)
        # Creat dirrectory for next category
        os.makedirs(output_directory, exist_ok=True)

# Example usage:
if __name__ == "__main__":
    download_files_from_yaml()
