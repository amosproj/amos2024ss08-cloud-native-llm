import landscape_explorer
import unittest
import mock
import landscape_explorer
from unittest.mock import Mock


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = {"Content-Type": "application/json"}

        def json(self):
            return self.json_data
    match args[0]:
        case 'https://api.github.com/repos/org/repo_good/git/trees/main?recursive=1':
            return MockResponse({
                "tree": [
                    {"path": "file1.yml", "type": "blob"},
                    {"path": "file2.md", "type": "blob"},
                ]
            }, 200)
        case 'https://api.github.com/repos/org/repo_nested/git/trees/main?recursive=1':
            return MockResponse({
                "tree": [
                    {"path": "file1.yml", "type": "blob"},
                    {"path": "tree_path1", "type": "tree", "sha": "tree_sha1"}
                ],
                "truncated": "true"
            }, 200)
        case 'https://api.github.com/repos/org/repo_nested/git/trees/main':
            return MockResponse({
                "tree": [
                    {"path": "file1.yml", "type": "blob"},
                    {"path": "file2.md", "type": "blob"},
                    {"path": "tree_path1", "type": "tree", "sha": "tree_sha1"}
                ]
            }, 200)
        case 'https://api.github.com/repos/org/repo_nested/git/trees/tree_sha1?recursive=1':
            return MockResponse({
                "tree": [
                    {"path": "file3.yml", "type": "blob"},
                    {"path": "tree_path2", "type": "tree", "sha": "tree_sha2"},
                ],
                "truncated": "true"}, 200)
        case 'https://api.github.com/repos/org/repo_nested/git/trees/tree_sha1':
            return MockResponse({
                "tree": [
                    {"path": "file3.yml", "type": "blob"},
                    {"path": "file4.md", "type": "blob"},
                    {"path": "tree_path2", "type": "tree", "sha": "tree_sha2"},
                ]}, 200)
        case 'https://api.github.com/repos/org/repo_nested/git/trees/tree_sha2?recursive=1':
            return MockResponse({
                "tree": [
                    {"path": "file5.yml", "type": "blob"},
                    {"path": "file6.md", "type": "blob"},
                ]}, 200)
    return MockResponse(None, 404)


class LandscapeExplorerTest(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls(self, mock_get):

        landscape_explorer.get_default_branch = Mock(return_value="main")

        result = landscape_explorer.get_urls(
            "https://github.com/org/repo_good")

        expected_result = {
            "yml": ["https://raw.githubusercontent.com/org/repo_good/main/file1.yml"],
            "md": ["https://raw.githubusercontent.com/org/repo_good/main/file2.md"]
        }
        self.assertEqual(result, expected_result)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_urls_with_nested_files(self, mock_get):

        landscape_explorer.get_default_branch = Mock(return_value="main")

        result = landscape_explorer.get_urls(
            "https://github.com/org/repo_nested")

        expected_result = {
            "yml": ["https://raw.githubusercontent.com/org/repo_nested/main/file1.yml",
                    "https://raw.githubusercontent.com/org/repo_nested/main/tree_path1/file3.yml",
                    "https://raw.githubusercontent.com/org/repo_nested/main/tree_path1/tree_path2/file5.yml"],
            "md": ["https://raw.githubusercontent.com/org/repo_nested/main/file2.md",
                   "https://raw.githubusercontent.com/org/repo_nested/main/tree_path1/file4.md",
                   "https://raw.githubusercontent.com/org/repo_nested/main/tree_path1/tree_path2/file6.md"]
        }

        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
