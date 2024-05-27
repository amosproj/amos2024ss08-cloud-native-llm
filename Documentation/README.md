Build, user, and technical documentation
Software architecture description

## Requirements

- Python3

Install the requirements by running the following command from the root file

```
pip install -r requirements.txt
```

## Creating YAML landscape file

To create a yaml file with the CNCF Lanscape follow this instructions:

1. Poblate with repository data

   1. You will need a Github token to access the API. Refer to [Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic). Copy and paste it in the appropiate location in the script landscape_explorer.py replacing "test_token".

   1. Go to the folder src/scripts

      ```
      cd src/scripts
      ```

   1. Execute landscape_explorer.py

      ```
      python landscape_explorer.py
      ```

1. Poblate with scraped data from websites

   1. Go to the folder src/landscape_scraper and execute

   ```
    scrapy crawl docs -O output.json
   ```

   2. Go to the folder src/scripts and execute:

   ```
    python augment_landscape.py
   ```

   3. The desired landscape_augmented_repos_websites.yml will be in the sources folder

## Running Entire ETL and QA Processes (Tested on Ubuntu 20.04, Compatible with Linux and macOS)

The 'run_all.sh' script automates environment setup, ETL processes, and Q&A generation tasks.

### Prerequisites

1. **Environment Variables**: Create a `.env` file in the root directory with the following content:

```text
GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>
HF_TOKEN=<YOUR_HUGGING_FACE_TOKEN>
```

Replace '<YOUR_GITHUB_TOKEN>' with your GitHub token obtained as described earlier, and '<YOUR_HUGGING_FACE_TOKEN>' with your Hugging Face token, which can be found at (https://huggingface.co/settings/tokens)

2. **Execute from Root Directory**: Run the script from the root directory of your project.

### Usage

```bash
./script.sh [etl] [qa] <data_set_id>
```

### Example

This command executes the ETL process, uploading the output to the specified dataset:

```bash
./script.sh SuperOrganization/WorldDataset
```
