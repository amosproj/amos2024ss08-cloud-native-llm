import unittest
import os
import json
import yaml
import tempfile
import shutil
from datetime import datetime
import PyPDF2
from src.scripts.Unified_format_conversation import (
    extract_metadata, convert_files_to_json, process_error_yaml_file
)

class TestFileProcessing(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.json_dir = os.path.join(self.test_dir, 'json_output')
        os.makedirs(self.json_dir, exist_ok=True)
        self.processed_files = set()
        self.error_file_list = []
        self.chunk_size = 4

        self.sample_yaml_file = os.path.join(self.test_dir, 'category_subcategory_project_sample.yaml')
        self.sample_md_file = os.path.join(self.test_dir, 'category_subcategory_project_sample.md')
        self.sample_pdf_file = os.path.join(self.test_dir, 'category_subcategory_project_sample.pdf')
        self.error_yaml_file = os.path.join(self.test_dir, 'category_subcategory_project_error.yaml')

        with open(self.sample_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump([{'step': 'first', 'description': 'This is the first step'}, {'step': 'second', 'description': 'This is the second step'}], f)

        with open(self.sample_md_file, 'w', encoding='utf-8') as f:
            f.write("# Heading 1\nContent under heading 1\n## Subheading 1.1\nContent under subheading 1.1\n #More Heading\n Content Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et")

        with open(self.sample_pdf_file, 'wb') as f:
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_blank_page(width=72, height=72)
            pdf_writer.write(f)

        with open(self.error_yaml_file, 'w', encoding='utf-8') as f:
            f.write("This is an invalid YAML content: {missing_quotes: value\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_extract_metadata(self):
        file_name = 'category_subcategory_project_file.txt'
        expected_metadata = {
            'category': 'category',
            'subcategory': 'subcategory',
            'project_name': 'project',
            'file_name': 'file.txt'
        }
        self.assertEqual(extract_metadata(file_name), expected_metadata)

    def test_convert_files_to_json(self):
        print(f"Test directory: {self.test_dir}")
        print(f"JSON output directory: {self.json_dir}")
        print(f"Files in test directory: {os.listdir(self.test_dir)}")

        convert_files_to_json(
            self.processed_files, 
            self.chunk_size, 
            self.error_file_list, 
            json_file_path=self.json_dir, 
            file_paths=self.test_dir
        )

        json_files = os.listdir(self.json_dir)
        print(f"JSON files created: {json_files}")

        self.assertIn('md_data.json', json_files)
        if 'yaml_data.json' not in json_files:
            print("yaml_data.json not created.")
        if 'pdf_data.json' not in json_files:
            print("pdf_data.json not created.")

        with open(os.path.join(self.json_dir, 'md_data.json'), 'r', encoding='utf-8') as f:
            md_data = json.load(f)
        self.assertEqual(len(md_data), 1)
        self.assertEqual(md_data[0]['tag']['file_name'], 'sample.md')

        if 'yaml_data.json' in json_files:
            with open(os.path.join(self.json_dir, 'yaml_data.json'), 'r', encoding='utf-8') as f:
                yaml_data = json.load(f)
            self.assertEqual(len(yaml_data), 1)
            self.assertEqual(yaml_data[0]['tag']['file_name'], 'sample.yaml')

        if 'pdf_data.json' in json_files:
            with open(os.path.join(self.json_dir, 'pdf_data.json'), 'r', encoding='utf-8') as f:
                pdf_data = json.load(f)
            self.assertEqual(len(pdf_data), 1)
            self.assertEqual(pdf_data[0]['tag']['file_name'], 'sample.pdf')


if __name__ == '__main__':
    unittest.main()
