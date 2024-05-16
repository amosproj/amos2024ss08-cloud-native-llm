from yaml.representer import Representer
from collections import defaultdict
import yaml
import collections
import ijson


yaml.add_representer(collections.defaultdict, Representer.represent_dict)
AUGMENTED_YAML_REPOS = '../../sources/landscape_augmented_repos.yml'
WEBSITE_URLS_PATH = '../landscape_scraper/websites_docs.json'
OUTPUT_PATH = '../../sources/landscape_augmented_repos_websites.yml'


def get_website_urls():
    with open(WEBSITE_URLS_PATH, 'r') as f:
        objects = ijson.items(f, 'item')
        urls = defaultdict(defaultdict)
        for obj in objects:
            if obj['origin_url'] not in urls or obj['type'] not in urls[obj['origin_url']]:
                urls[obj['origin_url']][obj['type']] = []
            urls[obj['origin_url']][obj['type']].append(obj['url'])
        return urls


def generate_augmented_yml_with_scraped_urls():
    website_urls = get_website_urls()
    with open(AUGMENTED_YAML_REPOS, 'r') as file:
        content = yaml.safe_load(file)
    for category in content.get('landscape'):
        for subcategory in category.get('subcategories'):
            for item in subcategory.get('items'):
                if 'homepage_url' not in item or not item.get('homepage_url'):
                    continue

                if item['homepage_url'] in website_urls:
                    item['website'] = defaultdict(list)
                    for type in website_urls[item['homepage_url']]:
                        item['website'][type] = website_urls[item['homepage_url']][type]

    with open(OUTPUT_PATH, 'w+') as file:
        yaml.dump(content, file, sort_keys=False)


if __name__ == '__main__':
    generate_augmented_yml_with_scraped_urls()
