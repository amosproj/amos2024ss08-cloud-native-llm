import requests
import yaml
import os

def download_files_from_yaml(yaml_file, output_directory):
    # Load URLs from YAML file
    with open(yaml_file, 'r') as f:
        urls = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Download files from URLs
    for i, url in enumerate(urls, start=1):
        try:
            # Send HTTP GET request to download the file
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Extract filename from URL
            filename = os.path.basename(url)

            # Write downloaded content to file
            with open(os.path.join(output_directory, filename), 'wb') as f:
                f.write(response.content)

            print(f"File {i}/{len(urls)} downloaded successfully: {filename}")

        except Exception as e:
            print(f"Failed to download file from {url}: {e}")

# Example usage:
yaml_file = 'urls.yaml'  # Path to YAML file containing URLs
output_directory = 'downloaded_files'  # Output directory to save downloaded files
download_files_from_yaml(yaml_file, output_directory)
