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

1. You will need a Github token to access the API. Refer to [Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic). Copy and paste it in the appropiate location in the script landscape_explorer.py replacing "test_token".

1. Go to the folder src/scripts

   ```
   cd src/scripts
   ```

1. Execute landscape_explorer.py

   ```
   python landscape_explorer.py
   ```

1. The folder "sources" in the root of the project will contain the desired file.
