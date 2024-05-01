import unittest
from unittest.mock import Mock

from landscape_explorer import get_urls
import landscape_explorer
import mock


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = {"Content-Type": "application/json"}

        def json(self):
            return self.json_data

    if args[0] == 'https://api.github.com/repos/org/repo_good/git/trees/main?recursive=1':
        return MockResponse({
            "tree": [
                {"path": "file1.yml", "type": "blob"},
                {"path": "file2.md", "type": "blob"},
            ]
        }, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse(None, 404)


class LandscapeExplorerTest(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls(self, mock_get):

        landscape_explorer.get_default_branch = Mock(return_value="main")

        result = get_urls("https://github.com/org/repo_good")

        expected_result = {
            "yml": ["https://raw.githubusercontent.com/org/repo_good/main/file1.yml"],
            "md": ["https://raw.githubusercontent.com/org/repo_good/main/file2.md"]
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
