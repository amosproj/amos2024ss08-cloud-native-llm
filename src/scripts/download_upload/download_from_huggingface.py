# This script loads datasets from specified files using the Hugging Face datasets library, with logging configured to track the process.

# Key Features:
# 1. Logging Configuration: Initializes logging to capture informational and error messages.
# 2. Dataset Loading: Utilizes the Hugging Face datasets library (`load_dataset`) to load datasets from JSON files.
# 3. Exception Handling: Catches and logs errors during dataset loading to provide detailed error messages.
# 4. Interrupt Handling: Handles KeyboardInterrupt to gracefully stop operations when requested by the user.

# Modules:
# - logging: Provides logging capabilities to track script execution and errors.
# - datasets: Import from Hugging Face datasets library for dataset loading.
# - pandas: For data manipulation and handling DataFrame output.

# Functions:
# - load_dataset_from_files(dataset_name, data_files, config_name): Loads datasets from JSON files based on specified dataset name and configuration.
# - get_dataset_config_names(dataset_name): Retrieves configuration names available for a given dataset.

# Execution:
# 1. Retrieves available configurations for the dataset "Kubermatic/cncf-raw-data-for-llm-training".
# 2. Loads datasets from "md_data.json" and "pdf_data.json" using the 'default' configuration.
# 3. Logs information about loaded datasets and prints them as Pandas DataFrames.
# 4. Handles exceptions such as configuration retrieval failure, dataset loading errors, and user interruptions.

import logging
from datasets import load_dataset, get_dataset_config_names
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("huggingface_hub.repocard").setLevel(logging.ERROR)

def load_dataset_from_files(dataset_name: str, data_files: Dict[str, str], config_name: str) -> Dict[str, dict]:
    """
    Load dataset from files with the specified configuration.

    Args:
        dataset_name (str): The name of the dataset to load.
        data_files (dict): A dictionary where keys are split names and values are file paths.
        config_name (str): The name of the configuration to use.

    Returns:
        dict: A dictionary containing loaded datasets for each split.
    """

    
    datasets = {}
    try:
        for split, file_name in data_files.items():
            dataset = load_dataset(dataset_name, config_name, data_files={split: file_name})
            datasets[split] = dataset
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
    return datasets

try:
    # Get all configurations for the specific dataset
    dataset_name = "Kubermatic/cncf-raw-data-for-llm-training"
    try:
        configs = get_dataset_config_names(dataset_name)
        logger.info(f"Available configurations for {dataset_name}: {configs}")
    except Exception as e:
        logger.error(f"Failed to retrieve configurations for {dataset_name}: {e}")
        configs = []

    # Since only 'default' is available, we use it
    config_name = 'default'

    # Define the unified data files name which will be used
    data_files = {
        "file1": "md_data.json",
        "file2": "pdf_data.json",
    }

    # Load the dataset
    try:
        datasets = load_dataset_from_files(dataset_name, data_files, config_name)
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        datasets = {}

    # Print the loaded datasets
    for split, dataset in datasets.items():
        logger.info(f"Dataset for {split} split:")
        df = dataset[split].to_pandas()
        print(df)
except KeyboardInterrupt:
    logger.info("Operation interrupted by user.")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
