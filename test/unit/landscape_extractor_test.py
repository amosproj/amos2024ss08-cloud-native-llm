import unittest
import os
import zipfile
import sys
import shutil

# Assuming landscape_extractor.py is located in the src/scripts/data_preparation directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.scripts.data_preparation import landscape_extractor

class Testdownload_files_from_yaml(unittest.TestCase):
    """
    In order to this test works you must add your gitHub token in landscape_extractor.py file
    """

    def setUp(self):
        self.output_directory = "sources/raw_files_test"
        self.cache_file = landscape_extractor.CACHE_FILE
        os.makedirs(self.output_directory, exist_ok=True)
        # Ensure the cache file is clean before each test
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def test_with_valid_input(self):
        expected_zipFile = "sources/Test_Provisioning.zip"
        # Write downloaded content to file
        landscape_extractor.download_files_from_yaml(
            yaml_file="amos2024ss08-cloud-native-llm/test/resources/test_landscape_augmented.yml", output_directory=self.output_directory)

        # Create the extract output_directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)
        # Open the zip file
        with zipfile.ZipFile(expected_zipFile, 'r') as zip_file:
            # Extract all the contents to the specified output_directory
            zip_file.extractall(self.output_directory)
        # Assert the file exists
        file_path_1 = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_bug_report.md"
        error_message_1 = f"File '{file_path_1}' was not downloaded."
        self.assertTrue(os.path.exists(file_path_1), error_message_1)
        
        file_path_2 = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_feature_request.md"
        error_message_2 = f"File '{file_path_2}' was not downloaded."
        self.assertTrue(os.path.exists(file_path_2), error_message_2)

    def test_cache_functionality(self):
        # Download files first time
        landscape_extractor.download_files_from_yaml(
            yaml_file="amos2024ss08-cloud-native-llm/test/resources/test_landscape_augmented.yml", output_directory=self.output_directory)
        
        # Capture the cache contents after the first download
        with open(self.cache_file, 'r') as f:
            initial_cache_contents = f.readlines()

        # Download files second time and capture cache contents again
        landscape_extractor.download_files_from_yaml(
            yaml_file="amos2024ss08-cloud-native-llm/test/resources/test_landscape_augmented.yml", output_directory=self.output_directory)

        with open(self.cache_file, 'r') as f:
            subsequent_cache_contents = f.readlines()

        # Assert the cache contents are the same, ensuring no duplicates were added
        self.assertEqual(initial_cache_contents, subsequent_cache_contents)

    def tearDown(self):
        # Clean up: remove the output_directory and its contents
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)
        if os.path.exists("sources/Test_Provisioning.zip"):
            os.remove("sources/Test_Provisioning.zip")
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        

if __name__ == '__main__':
    unittest.main()
