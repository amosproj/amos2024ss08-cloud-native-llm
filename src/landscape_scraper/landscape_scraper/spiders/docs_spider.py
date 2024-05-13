import scrapy.linkextractors
import yaml
import requests
import scrapy


BASE_REPO_YAML = 'https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml'


class QuotesSpider(scrapy.Spider):
    name = "docs"

    def __init__(self):
        self.link_extractor = scrapy.linkextractors.LinkExtractor(
            allow=".*doc.*")

    def start_requests(self):
        urls = []
        try:
            response = requests.get(BASE_REPO_YAML)
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to fetch {BASE_REPO_YAML}") from e

        content = response.content.decode('utf-8')
        content = yaml.safe_load(content)
        for category in content.get('landscape'):
            for subcategory in category.get('subcategories'):
                for item in subcategory.get('items'):
                    if 'homepage_url' not in item or not item.get('homepage_url'):
                        continue
                    urls.append(item.get('homepage_url'))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            yield {
                "doc_url": link.url,
            }
