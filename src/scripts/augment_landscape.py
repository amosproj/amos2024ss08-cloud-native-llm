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
    """
    Retrieves website URLs from a JSON file.

    Returns:
        defaultdict: A nested dictionary containing website URLs categorized by origin URL and type.
    """
    with open(WEBSITE_URLS_PATH, 'r') as f:
        objects = ijson.items(f, 'item')
        urls = defaultdict(defaultdict)
        for obj in objects:
            if obj['origin_url'] not in urls or obj['type'] not in urls[obj['origin_url']]:
                urls[obj['origin_url']][obj['type']] = []
            urls[obj['origin_url']][obj['type']].append(obj['url'])
        return urls


def generate_augmented_yml_with_scraped_urls():
    """
    Generates an augmented YAML file with scraped website URLs.

    This function reads the augmented YAML file, processes each category, subcategory, and item,
    and adds the corresponding website URLs from the scraped data. The augmented YAML file is then
    saved to the output path.
    """
    website_urls = get_website_urls()
    with open(AUGMENTED_YAML_REPOS, 'r') as file:
        content = yaml.safe_load(file)
    for category in content.get('landscape'):
        process_category(category, website_urls)
    with open(OUTPUT_PATH, 'w+') as file:
        yaml.dump(content, file, sort_keys=False)


def process_category(category, website_urls):
    """
    Processes a category in the augmented YAML file.

    Args:
        category (dict): The category dictionary.
        website_urls (defaultdict): The nested dictionary of website URLs.

    This function processes each subcategory in the category.
    """
    print(category)
    for subcategory in category.get('subcategories'):
        process_subcategory(subcategory, website_urls)


def process_subcategory(subcategory, website_urls):
    """
    Processes a subcategory in the augmented YAML file.

    Args:
        subcategory (dict): The subcategory dictionary.
        website_urls (defaultdict): The nested dictionary of website URLs.

    This function processes each item in the subcategory.
    """
    for item in subcategory.get('items'):
        process_item(item, website_urls)


def process_item(item, website_urls):
    """
    Processes an item in the augmented YAML file.

    Args:
        item (dict): The item dictionary.
        website_urls (defaultdict): The nested dictionary of website URLs.

    This function checks if the item has a homepage URL and if it exists in the website URLs.
    If so, it adds the corresponding website URLs to the item's 'website' attribute.
    """
    if 'homepage_url' not in item or not item.get('homepage_url'):
        return

    if item['homepage_url'] in website_urls:
        item['website'] = defaultdict(list)
        for type in website_urls[item['homepage_url']]:
            item['website'][type] = website_urls[item['homepage_url']][type]


if __name__ == '__main__':
    generate_augmented_yml_with_scraped_urls()
