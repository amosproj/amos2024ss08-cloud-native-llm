import requests
import yaml
import os
def downloader(download_urls, output_directory, tags_dict):
    for file_format, urls_list in download_urls.items():
        for url in urls_list:
            try:
                # Send HTTP GET request to download the file
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Extract filename from URL
                filename = os.path.basename(url)
                # Add tags to each filename
                # Seperate tags with "_"
                filename = tags_dict['Category'] +"_"+ tags_dict['Subcategory'] +"_"+ tags_dict['Project_name'] +"_"+ filename

                # Write downloaded content to file
                with open(os.path.join(output_directory, filename), 'wb') as f:
                    f.write(response.content)

                #print(f"File {i}/{len(urls)} downloaded successfully: {filename}")

            except Exception as e:
                print(f"Failed to download file from {url}: {e}")
        
    
def download_files_from_yaml(yaml_file = "sources/landscape_augmented.yml", output_directory = "sources/raw_files"):
    # Load URLs from YAML file
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {'Category': "", 'Subcategory': "", 'Project_name': ""}
    # Process the loaded data
    for category in data['landscape']:
        tags_dict['Category'] = category['name']
        print(f"Category: {tags_dict['Category']}")
        for subcategory in category.get('subcategories', []):
            tags_dict['Subcategory'] = subcategory['name']
            print(f"Subcategory: {tags_dict['Subcategory']}")
            for item in subcategory.get('items', []):
                tags_dict['Project_name'] = item['name']
                print(f"Item: {tags_dict['Project_name']}")
                downloader(item['download_urls'],output_directory, tags_dict)
            


    # Download files from URLs
    #for i, url in enumerate(urls, start=1):

# Example usage:
if __name__ == "__main__":
    download_files_from_yaml()
