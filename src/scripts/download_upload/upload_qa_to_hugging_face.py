import os
from tqdm import tqdm
from huggingface_hub import HfApi, login

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
HF_TOKEN = os.getenv("HF_TOKEN", "upload_your_hf_token_here")


def upload_QandA_to_huggingface(file_path, hf_dataset_id):
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
