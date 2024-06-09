import yaml
import os
import shutil
import requests
from bs4 import BeautifulSoup


def save_strings_to_md(string, output_dir, tags):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = os.path.join(
        output_dir,
        tags["Category"]
        + "_"
        + tags["Subcategory"]
        + "_"
        + tags["Project_name"]
        + ".md",
    )
    # Write the content to the file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(string)


def extract_text(links: list, output_directory: str, tags: dict):
    for url in links:

        # Send a GET request to the webpage
        response = requests.get(url)
        temp = ""

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content of the response with BeautifulSoup
            soup = BeautifulSoup(response.content, "lxml")

            body = soup.body
            if body:
                for element in body.descendants:
                    if element.name == "p":
                        temp += element.get_text()
                        temp += "\n"
                    elif element.name == "pre":
                        temp += "```\n" + element.get_text() + "```"
                        temp += "\n"

                # print(temp)
                save_strings_to_md(temp, output_directory, tags)
        else:
            print(
                f"Failed to retrieve the webpage. Status code: {response.status_code}"
            )


def download_files_from_yaml(
    yaml_file="../../sources/test_landscape_augmented.yml",
    output_directory="sources/raw_files",
):
    """
    Downloads the files with specific extensions from the URLs provided in yaml_file

    Args:
        yaml_file (str, optional): The path to the URLs yaml file(default: sources/landscape_augmented.yml).
        output_directory (str, optional): The path where the downloaded files will be stored(defult: sources/raw_files).

    """
    # Load URLs from YAML file
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    # Initialize a dictionary to save tags corresponding to each file
    tags_dict = {"Category": "", "Subcategory": "", "Project_name": ""}
    # Process the loaded data
    for category in data["landscape"]:
        # It downloads only below defined categories to avoid duplication
        category_list = [
            "App Definition and Development",
            "Orchestration & Management",
            "Runtime",
            "Provisioning",
            "Observability and Analysis",
            "Test_Provisioning",
        ]
        if category["name"] not in category_list:
            continue
        tags_dict["Category"] = category["name"]
        print(f"Category: {tags_dict['Category']}")
        for subcategory in category.get("subcategories", []):
            tags_dict["Subcategory"] = subcategory["name"]
            print(f"Subcategory: {tags_dict['Subcategory']}")
            for item in subcategory.get("items", []):
                tags_dict["Project_name"] = item["name"]
                print(f"Item: {tags_dict['Project_name']}")
                website = item.get("website", {})
                extract_text(website.get("docs", []), output_directory, tags_dict)
                
        # Adding all the files corresponding to a category to a zip file
        shutil.make_archive(
            "sources/" + tags_dict["Category"], "zip", output_directory + "/"
        )
        # Removing remminig raw files after archiving
        # shutil.rmtree(output_directory)
        # Creat dirrectory for next category
        os.makedirs(output_directory, exist_ok=True)


# Example usage:
if __name__ == "__main__":
    download_files_from_yaml()
