"""
This script facilitates uploading a CSV file to a Hugging Face dataset repository using the Hugging Face Hub API.

Dependencies:
- os
- tqdm
- huggingface_hub (imported as HfApi and login)

Functions:
- `upload_QandA_to_huggingface(file_path, hf_dataset_id)`: Uploads a CSV file to a specified Hugging Face dataset repository.

Usage Example:
- The script expects two arguments when executed:
  - `file_path`: The path to the CSV file to upload.
  - `hf_dataset_id`: The ID of the Hugging Face dataset repository where the file will be uploaded.
- It logs into Hugging Face using the `HF_TOKEN` environment variable (or a default token if not set).
- It uploads the specified CSV file to the specified dataset repository.
- Progress of the upload is displayed using a tqdm progress bar.

Notes:
- Ensure the environment variable `HF_TOKEN` is set to your Hugging Face API token or provide it directly in the script.
- The script uses `os.path.basename(file_path)` to determine the file name in the repository.
- The repository type is specified as "dataset" during the upload.

"""

import os
from tqdm import tqdm
from huggingface_hub import HfApi, login

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
HF_TOKEN = os.getenv("HF_TOKEN", "upload_your_hf_token_here")


def upload_QandA_to_huggingface(file_path: str, hf_dataset_id: str) -> None:
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
    login(token=HF_TOKEN)

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
    upload_QandA_to_huggingface(
        "qa_generation/questions.csv", "Kubermatic/cncf-raw-data-for-llm-training")
