from yaml.representer import Representer
from collections import defaultdict
import yaml
import collections
import ijson


yaml.add_representer(collections.defaultdict, Representer.represent_dict)
AUGMENTED_YAML = '../../sources/landscape_augmented.yml'
WEBSITE_URLS_PATH = '../landscape_scraper/websites_docs.json'


def get_website_urls():
    with open(WEBSITE_URLS_PATH, 'r') as f:
        objects = ijson.items(f, 'item')
        urls = defaultdict(defaultdict)
        for obj in objects:
            if obj['origin_url'] not in urls or obj['type'] not in urls[obj['origin_url']]:
                urls[obj['origin_url']][obj['type']] = []
            urls[obj['origin_url']][obj['type']].append(obj['doc_url'])
        return urls


def generate_augmented_yml_with_scraped_urls():
    website_urls = get_website_urls()
    with open(AUGMENTED_YAML, 'r') as file:
        content = yaml.safe_load(file)
    for category in content.get('landscape'):
        for subcategory in category.get('subcategories'):
            for item in subcategory.get('items'):
                if 'homepage_url' not in item or not item.get('homepage_url'):
                    continue

                if item['homepage_url'] in website_urls:
                    item['website'] = defaultdict(list)
                    item['website']['docs'] = website_urls[item['homepage_url']]['doc']

    with open('../../sources/landscape_augmented.yml', 'w+') as file:
        yaml.dump(content, file, sort_keys=False)


if __name__ == '__main__':
    generate_augmented_yml_with_scraped_urls()
