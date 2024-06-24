import unittest
import os
import shutil
import sys
# Add the root of the project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.scripts.data_preparation import webpages_extractor

class Testdownload_files_from_yaml(unittest.TestCase):

    def test_with_valid_input(self):
        output_directory = "sources/raw_files_test"
        os.makedirs(output_directory, exist_ok=True)

        # Write downloaded content to file
        webpages_extractor.download_files_from_yaml(
            yaml_file=os.path.join(os.path.dirname(__file__), '../resources/test_landscape_augmented.yml'), output_directory=output_directory)

        # Assert the file exists
        file_path_1 = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_get_started_inventory.html.md"
        error_message_1 = f"File '{file_path_1}' was not downloaded."
        self.assertTrue(os.path.exists(file_path_1), error_message_1)
        
        file_path_2 = "sources/raw_files_test/Test_Provisioning_Automation & Configuration_Airship_release_and_maintenance.html.md"
        error_message_2 = f"File '{file_path_2}' was not downloaded."
        self.assertTrue(os.path.exists(file_path_2), error_message_2)

        # Test cache functionality: download again and check if skipped
        webpages_extractor.download_files_from_yaml(
            yaml_file=os.path.join(os.path.dirname(__file__), '../resources/test_landscape_augmented.yml'), output_directory=output_directory)

        # Assert nothing new was downloaded (since it should be cached)
        new_file_path = "sources/raw_files_test/New_Test_File.html.md"
        self.assertFalse(os.path.exists(new_file_path), f"Unexpected download of '{new_file_path}'")

    def tearDown(self):
        # Clean up: remove the output_directory and its contents
        output_directory = "sources/raw_files_test/"
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        if os.path.exists("sources/webpages_documentations.zip"):
            os.remove("sources/webpages_documentations.zip")
        if os.path.exists(webpages_extractor.CACHE_FILE):
            os.remove(webpages_extractor.CACHE_FILE)
        # if os.path.exists("test/resources/test_landscape_augmented.yml"):
        #     os.remove("test/resources/test_landscape_augmented.yml")

    def test_google_doc_to_pdf_conversion(self):
        output_directory = "sources/raw_files_test"
        os.makedirs(output_directory, exist_ok=True)

        # Mock URL to a Google Doc
        google_doc_url = "https://docs.google.com/document/d/example_document_id/edit"

        # Download the Google Doc (PDF conversion)
        webpages_extractor.save_doc_to_pdf(google_doc_url, output_directory, {
            "Category": "Test_Category",
            "Subcategory": "Test_Subcategory",
            "Project_name": "Test_Project",
            "filename": "test_google_doc"
        })

        # Assert the PDF file exists in the output directory
        pdf_file_path = os.path.join(output_directory, "Test_Category_Test_Subcategory_Test_Project_test_google_doc.pdf")
        self.assertTrue(os.path.exists(pdf_file_path), f"PDF file '{pdf_file_path}' was not downloaded.")

if __name__ == '__main__':
    unittest.main()
