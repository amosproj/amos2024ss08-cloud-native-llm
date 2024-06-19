# This script uploads a CSV file to a Hugging Face dataset repository using the Hugging Face Hub API, with progress tracking displayed in a tqdm progress bar.

# Key Features:
# 1. Sets environment variable `HF_HUB_ENABLE_HF_TRANSFER` to enable Hugging Face transfer for uploads.
# 2. upload_QandA_to_huggingface() to upload a specified CSV file to a Hugging Face dataset repository.
# 3. Authentication: Uses Hugging Face API token for authentication via `login()` function from `huggingface_hub`.
# 4. File Upload: Utilizes `HfApi.upload_file()` method to transfer the CSV file to the specified dataset repository.

# Modules:
# - os: Provides functionality for interacting with the operating system, specifically for setting environment variables.
# - tqdm: Offers a customizable progress bar for tracking tasks.
# - huggingface_hub: Imports `HfApi` and `login` for interfacing with the Hugging Face Hub API.

# Functions:
# - upload_QandA_to_huggingface(file_path, hf_token, hf_dataset_id): Handles the process of logging in, uploading the CSV file, and displaying upload progress.

# Execution:
# - The script can be executed directly to upload a CSV file specified by `file_path` to the Hugging Face dataset repository identified by `hf_dataset_id`.
# - Progress updates are shown in the tqdm progress bar, providing feedback on the upload process.

import os
from tqdm import tqdm
from huggingface_hub import HfApi, login

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

def upload_QandA_to_huggingface(file_path: str, hf_token: str, hf_dataset_id: str) -> None:

    """
    Uploads a CSV file to a Hugging Face dataset repository.

    Args:
        file_path (str): The path to the CSV file to be uploaded.
        hf_token (str): The Hugging Face API token for authentication.
        hf_dataset_id (str): The ID of the Hugging Face dataset repository where the file will be uploaded.

    Returns:
        None

    This function performs the following steps:
    1. Logs into Hugging Face using the provided API token.
    2. Uploads the specified CSV file to the specified Hugging Face dataset repository.

    The progress of the file upload is displayed using a progress bar.

    Example:
        upload_QandA_to_huggingface("path/to/file.csv", "hf_example_token", "user/dataset_name")
    """

    api = HfApi()
    login(token=hf_token)
    
    # Upload the CSV file
    with tqdm(total=1, desc="Uploading CSV file") as pbar:
        api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo=os.path.basename(file_path),
            repo_id=hf_dataset_id,
            repo_type="dataset",
        )
        pbar.update(1)

if __name__ == "__main__":
    upload_QandA_to_huggingface("questions.csv", "Your Hugging Face authentication token", "huggingface dataset id")
