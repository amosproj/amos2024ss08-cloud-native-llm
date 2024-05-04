import requests
import yaml
import os
def downloader(download_urls, output_directory):
    for file_format, urls_list in download_urls.items():
        for url in urls_list:
            try:
                # Send HTTP GET request to download the file
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Extract filename from URL
                filename = os.path.basename(url)

                # Write downloaded content to file
                with open(os.path.join(output_directory, filename), 'wb') as f:
                    f.write(response.content)

                #print(f"File {i}/{len(urls)} downloaded successfully: {filename}")

            except Exception as e:
                print(f"Failed to download file from {url}: {e}")
        
    
def download_files_from_yaml(yaml_file = "sources/landscape_augmented.yml", output_directory = "sources/"):
    # Load URLs from YAML file
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # Process the loaded data
    for category in data['landscape']:
        print(f"Category: {category['name']}")
        for subcategory in category.get('subcategories', []):
            print(f"  Subcategory: {subcategory['name']}")
            for item in subcategory.get('items', []):
                print(f"    Item: {item['name']}")
                downloader(item['download_urls'],output_directory)
            


    # Download files from URLs
    #for i, url in enumerate(urls, start=1):

# Example usage:
if __name__ == "__main__":
    download_files_from_yaml()
