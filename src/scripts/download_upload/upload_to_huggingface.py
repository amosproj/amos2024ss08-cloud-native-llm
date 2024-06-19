# This script automates the process of uploading JSON files from a specified directory and its subdirectories to a Hugging Face dataset repository.

# Key Features:
# 1. Sets environment variable `HF_HUB_ENABLE_HF_TRANSFER` to enable Hugging Face transfer for uploads.
# 2. upload_to_huggingface() to discover JSON files recursively in a directory and upload them to a Hugging Face dataset.
# 3. Authentication: Uses Hugging Face API token for authentication via `login()` function from `huggingface_hub`.
# 4. File Discovery: Utilizes `os.walk()` to traverse the directory and identify JSON files for upload.
# 5. File Upload: Utilizes `HfApi.upload_file()` method to transfer each discovered JSON file to the specified dataset repository.

# Modules:
# - os: Provides functionality for interacting with the operating system, specifically for file and directory operations.
# - tqdm: Offers a customizable progress bar for tracking tasks.
# - subprocess: Enables running subprocesses, although not directly used in this script.
# - argparse: Facilitates parsing command-line arguments.
# - huggingface_hub: Imports `HfApi` and `login` for interfacing with the Hugging Face Hub API.

# Functions:
# - upload_to_huggingface(directory_path, hf_token, hf_dataset_id): Implements the logic to discover JSON files, authenticate, and upload them to the specified Hugging Face dataset.

# Execution:
# - The script can be executed directly or through command-line interface (CLI) with optional arguments for `hf_token`, `hf_dataset_id`, and `directory_path`.
# - Progress updates are shown in the tqdm progress bar, providing feedback on each JSON file upload.


import os
from tqdm import tqdm
import subprocess
import argparse
from huggingface_hub import HfApi, login

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

def upload_to_huggingface(directory_path: str, hf_token: str, hf_dataset_id: str) -> None:
    """
    Find json files in the directory and its subdirectories then upload them to the specified huggingface dataset.

    args:
        directory_path:     Path to the local directory of the data
        hf_token:           Account token of huggingface; used to authenticate: Find under: https://huggingface.co/settings/tokens
        hf_dataset_id:      ID of the huggingface dataset, i.e. kubermatic/CNCF-Documentation-Data

    returns:
        Nothing
    """
    json_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    api = HfApi()
    login(hf_token, add_to_git_credential = True)
    # Upload json files
    for json_file in tqdm(json_files):
        api.upload_file(
            path_or_fileobj=json_file,
            path_in_repo=json_file.split("/")[-1],
            repo_id=hf_dataset_id,
            repo_type="dataset",
        )

def main():
    """
    Main Function to parse cli arguments and to call the upload function:
    Example usage:
    python upload_to_huggingface.py ~/sampledirectory/ hf_dNUFWcaFAHDLnwJkbLqwwNChcgYXmDwu kubermatic/CNCF-Documentation-Data
    Obviously use our own token and own directory etc. This is just an example that wont work :)
    """
    parser = argparse.ArgumentParser(description="Upload markdown and PDF files to a dataset in Hugging Face Model Hub")
    parser.add_argument("hf_token", type=str, help="Your Hugging Face authentication token")
    parser.add_argument("hf_dataset_id", type=str, help="ID of the dataset you want to upload files to")
    parser.add_argument("--directory_path", type=str, default = "sources/unified_files", help="Path to the directory containing json files")
    args = parser.parse_args()

    upload_to_huggingface(args.directory_path, args.hf_token, args.hf_dataset_id)

if __name__ == "__main__":
    main()
