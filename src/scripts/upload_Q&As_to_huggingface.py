import os
from tqdm import tqdm
from huggingface_hub import HfApi, login

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

def upload_QandAs_to_huggingface(directory_path, hf_token, hf_dataset_id):

    """
    Uploads CSV files from a specified directory to a Hugging Face dataset repository.

    Args:
        directory_path (str): The path to the directory containing the CSV files to be uploaded.
        hf_token (str): The Hugging Face API token for authentication.
        hf_dataset_id (str): The ID of the Hugging Face dataset repository where the files will be uploaded.

    Returns:
        None

    This function performs the following steps:
    1. Searches for all CSV files in the specified directory and its subdirectories.
    2. Logs into Hugging Face using the provided API token.
    3. Uploads each CSV file to the specified Hugging Face dataset repository.

    The progress of the file uploads is displayed using a progress bar.

    Example:
        upload_QandAs_to_huggingface("directory path", "hf_example_token", "user/dataset_name")
    """
 
    csv_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    api = HfApi()
    login(token=hf_token)
    
    # Upload CSV files
    for csv_file in tqdm(csv_files):
        api.upload_file(
            path_or_fileobj=csv_file,
            path_in_repo=os.path.basename(csv_file),
            repo_id=hf_dataset_id,
            repo_type="dataset",
        )

   
if __name__ == "__main__":
     upload_QandAs_to_huggingface("directory_path where Q&As files contain", "Your Hugging Face authentication token", "hugging face dataset id")

