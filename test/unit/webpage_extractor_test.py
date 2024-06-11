import unittest
import os
from src.scripts import webpages_extractor
#import webpages_extractor


class Testdownload_files_from_yaml(unittest.TestCase):

    def test_with_valid_input(self):
        output_directory = "sources/raw_files_test"
        os.makedirs(output_directory, exist_ok=True)
        print("something")
        # Write downloaded content to file
        webpages_extractor.download_files_from_yaml(
            yaml_file="test/resources/test_landscape_augmented.yml", output_directory=output_directory)
        # Assert the file exists
        file_path = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_get_started_inventory.html.md"
        error_message = f"File '{file_path}' was not downloaded."
        self.assertTrue(os.path.exists(file_path), error_message)
        file_path = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_release_and_maintenance.html.md"
        error_message = f"File '{file_path}' was not downloaded."
        self.assertTrue(os.path.exists(file_path), error_message)

    def tearDown(self):
        # Clean up: remove the output_directory and its contents
        output_directory = "sources/raw_files_test/"
        if os.path.exists(output_directory):
            for filename in os.listdir(output_directory):
                os.remove(os.path.join(output_directory, filename))
            os.rmdir(output_directory)
        if os.path.exists("sources/Test_Provisioning.zip"):
            os.remove("sources/Test_Provisioning.zip")
        if os.path.exists("sources/test_landscape_augumented.yml"):
            os.remove("sources/test_landscape_augumented.yml")


if __name__ == '__main__':
    unittest.main()
