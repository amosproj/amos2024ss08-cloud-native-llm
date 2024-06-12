import unittest
from unittest.mock import patch, MagicMock, mock_open
import requests
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import yaml
import tempfile

API_KEY = 'test_api_key'
REQUEST_DELAY = 0
PROGRESS_FILE = 'test_progress.json'
CSV_FILE = 'test_qas.csv'
PROCESSED_IDS_FILE = 'test_processed_question_ids.json'
TAGS_FILE = 'test_tags.json'
TAGS_UPDATE_INTERVAL = 7
DAILY_REQUEST_LIMIT = 3000

from src.scripts.stackoverflow_extractor import fetch_with_backoff, qa_extractor, fetch_answers, remove_html_tags, save_to_csv, load_tags

class TestStackOverflowQAScript(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.progress_file = os.path.join(self.temp_dir.name, 'test_progress.json')
        self.csv_file = os.path.join(self.temp_dir.name, 'test_qas.csv')
        self.processed_ids_file = os.path.join(self.temp_dir.name, 'test_processed_question_ids.json')
        self.tags_file = os.path.join(self.temp_dir.name, 'test_tags.json')

        global PROGRESS_FILE, CSV_FILE, PROCESSED_IDS_FILE, TAGS_FILE
        PROGRESS_FILE = self.progress_file
        CSV_FILE = self.csv_file
        PROCESSED_IDS_FILE = self.processed_ids_file
        TAGS_FILE = self.tags_file

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('requests.get')
    def test_fetch_with_backoff_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        api_url = "http://example.com"
        params = {}

        response = fetch_with_backoff(api_url, params)
        self.assertEqual(response, {"items": []})

    @patch('requests.get')
    def test_fetch_with_backoff_rate_limit(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'retry-after': '1'}
        mock_get.return_value = mock_response

        api_url = "http://example.com"
        params = {}

        with self.assertRaises(SystemExit):
            fetch_with_backoff(api_url, params)

    @patch('requests.get')
    def test_qa_extractor(self, mock_get):
        mock_response_questions = MagicMock()
        mock_response_questions.status_code = 200
        mock_response_questions.json.return_value = {
            "items": [
                {"question_id": 1, "body": "<p>Question</p>", "answer_count": 1}
            ],
            "has_more": False
        }
        mock_response_answers = MagicMock()
        mock_response_answers.status_code = 200
        mock_response_answers.json.return_value = {
            "items": [
                {"body": "<p>Answer</p>", "score": 1}
            ]
        }

        mock_get.side_effect = [mock_response_questions, mock_response_answers]

        with patch('stackoverflow_extractor.fetch_answers', return_value=[{"body": "<p>Answer</p>", "score": 1}]):
            with patch('stackoverflow_extractor.load_processed_question_ids', return_value=set()):
                with patch('stackoverflow_extractor.save_processed_question_ids'):
                    with patch('stackoverflow_extractor.save_to_csv'):
                        request_count = 0
                        tag = "test"
                        start_page = 1
                        new_request_count = qa_extractor(request_count, tag, start_page)
                        self.assertEqual(new_request_count, 2)

    def test_remove_html_tags(self):
        html = "<p>This is a <b>test</b>.</p>"
        text = remove_html_tags(html)
        self.assertEqual(text, "This is a test.")

    def test_save_to_csv(self):
        data = [{"question": "Q1", "answer": "A1", "tag": "test"}]
        save_to_csv(data, CSV_FILE)

        df = pd.read_csv(CSV_FILE)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['question'], "Q1")
        self.assertEqual(df.iloc[0]['answer'], "A1")
        self.assertEqual(df.iloc[0]['tag'], "test")

    @patch('builtins.open', new_callable=mock_open, read_data='{"tags": ["test"], "last_update": "2023-01-01"}')
    def test_load_tags_from_json(self, mock_file):
        with patch('os.path.exists', return_value=True):
            with patch('json.load', return_value={'tags': ['test'], 'last_update': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")}):
                tags = load_tags()
                self.assertEqual(tags, ['test'])

    @patch('yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open, read_data='landscape:\n  - name: "App Definition and Development"\n    subcategories:\n      - items:\n          - name: "Project (description)"')
    def test_load_tags_from_yaml(self, mock_file, mock_yaml_load):
        mock_yaml_load.return_value = {
            'landscape': [
                {
                    'name': 'App Definition and Development',
                    'subcategories': [
                        {
                            'items': [
                                {'name': 'Project (description)'}
                            ]
                        }
                    ]
                }
            ]
        }

        with patch('os.path.exists', return_value=False):
            tags = load_tags()
            self.assertEqual(tags, ['Project'])

if __name__ == '__main__':
    unittest.main()
