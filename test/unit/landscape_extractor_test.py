import unittest
import os
from src.scripts import landscape_extactor
#from landscape_extactor import download_files_from_yaml
import zipfile


class Testdownload_files_from_yaml(unittest.TestCase):
    """
    In order to this test works you must add your gitHub token in landscape_extractor.py file


    """

    def test_with_valid_input(self):
        output_directory = "sources/raw_files_test"
        os.makedirs(output_directory, exist_ok=True)
        print("soomething")
        expected_zipFile = "sources/Test_Provisioning.zip"
        # Write downloaded content to file
        landscape_extactor.download_files_from_yaml(
            yaml_file="test/resources/test_landscape_augmented.yml", output_directory=output_directory)

        # Create the extract output_directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        # Open the zip file
        with zipfile.ZipFile(expected_zipFile, 'r') as zip_file:
            # Extract all the contents to the specified output_directory
            zip_file.extractall(output_directory)
        # Assert the file exists
        file_path = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_bug_report.md"
        error_message = f"File '{file_path}' was not downloaded."
        self.assertTrue(os.path.exists(file_path), error_message)
        file_path = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_feature_request.md"
        error_message = f"File '{file_path}' was not downloaded."
        self.assertTrue(os.path.exists(file_path), error_message)

  #  def tearDown(self):
  #      # Clean up: remove the output_directory and its contents
  #      output_directory = "sources/raw_files_test/"
  #      if os.path.exists(output_directory):
  #          for filename in os.listdir(output_directory):
  #              os.remove(os.path.join(output_directory, filename))
  #          os.rmdir(output_directory)
  #      if os.path.exists("sources/Test_Provisioning.zip"):
  #          os.remove("sources/Test_Provisioning.zip")
  #      if os.path.exists("sources/test_landscape_augumented.yml"):
  #          os.remove("sources/test_landscape_augumented.yml")


if __name__ == '__main__':
    unittest.main()
