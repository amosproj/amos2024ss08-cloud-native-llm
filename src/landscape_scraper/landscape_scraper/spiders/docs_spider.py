import scrapy.linkextractors
import yaml
import requests
import scrapy
from scrapy_splash import SplashRequest


BASE_REPO_YAML = 'https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml'


class QuotesSpider(scrapy.Spider):
    name = "docs"

    def __init__(self):
        self.link_extractor = scrapy.linkextractors.LinkExtractor(
            allow=[".*docs.*", ".*\.pdf$"])

    def start_requests(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
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
            #         break
            #     break
            # break

        for url in urls:
            yield SplashRequest(url, self.parse, headers=headers)

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            if link.url.endswith('.pdf'):
                yield {
                    "pdf_url": link.url,
                }
            else:
                yield {
                    "doc_url": link.url,
                }
