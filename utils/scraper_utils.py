import json
import uuid
import requests
from datetime import datetime, timedelta
import sys
import re
import os
import configparser
from urllib import parse
try:
    from tqdm import tqdm
except:
    print("Module 'tqdm' is not installed. Using default progress indicator.")


def filter_json_by_created_utc(json_data, min_created_utc, max_created_utc):
    def filter_children(children):
        return [child for child in children if "data" not in child or
                "created_utc" not in child["data"] or
                min_created_utc <= child["data"]["created_utc"] <= max_created_utc]

    if "data" in json_data and "children" in json_data["data"]:
        children = json_data["data"]["children"]
        filtered_children = filter_children(children)
        filtered_json = json_data.copy()
        filtered_json["data"]["children"] = filtered_children
        return filtered_json
    else:
        print("JSON Format not valid")
        return None



def download_image(script_dir: str, output_dir_name:str, url: str, subdirectory: str = ""):
    img_data = requests.get(url).content
    
    # Ensure the directory exists
    target_dir = os.path.join(script_dir, output_dir_name, subdirectory)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Create the full file path
    file_path = os.path.join(target_dir, str(uuid.uuid4()) + '.png')

    with open(file_path, 'wb') as handler:
        handler.write(img_data)



def slugify(input_string):
    stringa_modificata = input_string.replace(" ", "_")
    stringa_modificata = re.sub(r'[^a-zA-Z0-9_]', '', stringa_modificata)
    return stringa_modificata



def default_progress_bar(iteration, total, bar_length=50):
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    filled_length = int(bar_length * iteration // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\rProgress: |{bar}| {percent}% Complete', end='\r')