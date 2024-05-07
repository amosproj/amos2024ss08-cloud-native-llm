import os
from tqdm import tqdm
import subprocess
import argparse

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

def upload_to_huggingface(directory_path, hf_token, hf_dataset_id):
    """
    Find markdown and PDF files in the directory and its subdirectories then upload them to the specified huggingface dataset.

    args:
        directory_path:     Path to the local directory of the data
        hf_token:           Account token of huggingface; used to authenticate: Find under: https://huggingface.co/settings/tokens
        hf_dataset_id:      ID of the huggingface dataset, i.e. kubermatic/CNCF-Documentation-Data

    returns:
        Nothing
    """
    markdown_files = []
    pdf_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
            elif file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    # Upload markdown files
    for markdown_file in tqdm(markdown_files):
        cmd = f"huggingface-cli upload --repo-type dataset --token {hf_token} {hf_dataset_id} {markdown_file}"
        subprocess.run(cmd, shell=True)

    # Upload PDF files
    for pdf_file in tqdm(pdf_files):
        cmd = f"huggingface-cli upload --repo-type dataset --token {hf_token} {hf_dataset_id} {pdf_file}"
        subprocess.run(cmd, shell=True)

def main():
    """
    Main Function to parse cli arguments and to call the upload function:
    Example usage:
    python upload_to_huggingface.py ~/sampledirectory/ hf_dNUFWcaFAHDLnwJkbLqwwNChcgYXmDwu kubermatic/CNCF-Documentation-Data
    Obviously use our own token and own directory etc. This is just an example that wont work :)
    """
    parser = argparse.ArgumentParser(description="Upload markdown and PDF files to a dataset in Hugging Face Model Hub")
    parser.add_argument("directory_path", type=str, help="Path to the directory containing markdown and PDF files")
    parser.add_argument("hf_token", type=str, help="Your Hugging Face authentication token")
    parser.add_argument("hf_dataset_id", type=str, help="ID of the dataset you want to upload files to")
    args = parser.parse_args()

    upload_to_huggingface(args.directory_path, args.hf_token, args.hf_dataset_id)

if __name__ == "__main__":
    main()
