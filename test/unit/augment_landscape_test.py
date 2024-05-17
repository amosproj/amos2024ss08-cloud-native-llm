import unittest
import mock
from src.scripts import augment_landscape
from mock import Mock


class AugmentLandscapeTest(unittest.TestCase):
    ORIGIN_URL = 'https://www.zalando.de/'
    MOCK_SCRAPED_DATA = f'[{{"origin_url": "{ORIGIN_URL}", "type": "docs", "url": "https://www.zalando.de/docs"}}, {{"origin_url":  "{ORIGIN_URL}", "type": "pdfs", "url": "https://www.zalando.de/ai_test.pdf"}}, {{"origin_url":  "{ORIGIN_URL}", "type": "mds", "url": "https://www.zalando.de/instructions.md"}}]'

    @ mock.patch('builtins.open', mock.mock_open(read_data=MOCK_SCRAPED_DATA))
    def test_generate_augmented_yml_with_scraped_urls(self):

        mock_load_yaml = {
            "landscape": [
                {

                    "subcategories": [
                        {
                            "items": [
                                {
                                    "homepage_url": AugmentLandscapeTest.ORIGIN_URL,
                                    "repo:": {
                                        "download_urls": {
                                            "yml": ["https://raw.githubusercontent.com/org/repo_test/main/file1.yml"],
                                            "md": ["https://raw.githubusercontent.com/org/repo_test/main/file2.md"]

                                        }
                                    }
                                }
                            ]

                        }

                    ]

                }
            ]
        }
        augment_landscape.yaml.safe_load = Mock(return_value=mock_load_yaml)
        augment_landscape.generate_augmented_yml_with_scraped_urls()

        self.assertEqual(mock_load_yaml["landscape"][0]["subcategories"][0]
                         ["items"][0]["website"]["docs"], ["https://www.zalando.de/docs"])
        self.assertEqual(mock_load_yaml["landscape"][0]["subcategories"][0]["items"][0]["website"]["pdfs"], [
                         "https://www.zalando.de/ai_test.pdf"])
        self.assertEqual(mock_load_yaml["landscape"][0]["subcategories"][0]["items"][0]["website"]["mds"], [
                         "https://www.zalando.de/instructions.md"])


if __name__ == '__main__':
    unittest.main()
