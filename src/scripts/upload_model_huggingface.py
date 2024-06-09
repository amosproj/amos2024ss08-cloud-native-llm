from huggingface_hub import HfApi, login
import os
import sys
from tqdm import tqdm

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
HF_TOKEN = os.getenv("HF_TOKEN", "upload_your_hf_token_here")


def get_file_paths(directory_path, base_path="", res=None):
    """
    Recursively retrieves the file paths within a directory.

    Args:
      directory_path (str): The path to the directory.
      base_path (str, optional): The base path to prepend to the file paths. Defaults to "".
      res (list, optional): The list to store the file paths. Defaults to None.

    Returns:
      list: A list of file paths within the directory.
    """
    if res is None:
        res = []

    for element in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, element)):
            res.append("/".join([base_path, element])
                       if base_path else element)
        else:
            get_file_paths(os.path.join(directory_path, element),
                           "/".join([base_path, element])
                           if base_path else element, res)

    return res


def upload_files_to_huggingface(files, repo_id, directory_path):
    """
    Uploads files to a Hugging Face model repository.

    Args:
      files (list): A list of file names to be uploaded.
      repo_id (str): The ID of the Hugging Face model repository.
      directory_path (str): The directory path where the files are located.

    Returns:
      None
    """

    api = HfApi()
    login(token=HF_TOKEN, add_to_git_credential=True)

    # check if the repo_id has type model
    author = repo_id.split("/")[0]
    # get all models of the author
    models_id = set()
    for model in api.list_models(author=author):
        models_id.add(model.id)

    if repo_id not in models_id:
        print("The repo_id does not correspond to a model")
        sys.exit(1)

    for file in tqdm(files):
        print(
            f"Uploading {file} with path {os.path.join(directory_path, file)}")
        api.upload_file(
            path_or_fileobj=os.path.join(directory_path, file),
            path_in_repo=file,
            repo_id=repo_id
        )


if __name__ == "__main__":
    # get first two arguments from the command line, path of directory and dataset id
    try:
        directory_path = sys.argv[1]
        repo_id = sys.argv[2]
    except IndexError:
        print("Please provide the path of the directory and the dataset id")
        sys.exit(1)

    f = get_file_paths(directory_path)
    print(f)
    upload_files_to_huggingface(f, repo_id, directory_path)
