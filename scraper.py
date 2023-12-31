import json
import uuid
import requests
from datetime import datetime, timedelta
import sys
import re
import os
import configparser
tqdm_installed = True
try:
    from tqdm import tqdm
except:
    print("Module 'tqdm' is not installed. Using default progress indicator.")
    tqdm_installed = False
from utils.scraper_utils import *

progress = 0
def update_progress(new_value: int):
    global progress
    progress = new_value


def main():
    # Get the directory of the current script [Windows Compatibility]
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ini file parsing
    config = configparser.ConfigParser()
    config.read(script_dir + '/appconfig.ini')

    output_dir_name = config.get('scraper_configuration', 'output_dir_name')
    backward_days = config.getint('scraper_configuration', 'backward_days')
    subreddit_name = config.get("scraper_configuration", "subreddit_name")
    # api doc: https://old.reddit.com/dev/api/
    url = "https://reddit.com/r/"+subreddit_name.strip() +".json"
    headers = {"User-Agent": "Mozilla/5.0"}

    current_posts = requests.get(url, headers=headers).json()
    current_timestamp = int(datetime.now().timestamp())
    date_from_timestamp = (datetime.now() - timedelta(days=backward_days)).timestamp()

    url_list = []
    more_pages = True
    while True:
        current_posts = filter_json_by_created_utc(current_posts, date_from_timestamp, current_timestamp)
        if len(current_posts["data"]["children"]) == 0:
            print("No more posts to download in specified range.")
            break

        for index, single_post in enumerate(current_posts["data"]["children"]):
            url = single_post["data"]["url"]
            if "gallery" in url:
                media_metadata_dict = single_post["data"]['media_metadata']
                dict_keys = media_metadata_dict.keys()
                for index, id in enumerate(dict_keys):
                    image_type = media_metadata_dict[id]['m'].split('/')[1]
                    url = f"https://i.redd.it/{id}.{image_type}"
                    url_list.append(url)

            if len(current_posts) != 0:
                url_list.append(url)
            else:
                print("Downloaded all images from the specified date up until today.")
                more_pages = False

        if not more_pages:
            break

        url = "https://reddit.com/r/"+subreddit_name.strip()+".json?after=" + current_posts["data"]["after"]
        print("Getting to the next page at URL: " + url)
        current_posts = requests.get(url, headers=headers).json()
        if not current_posts:
            break

    total_urls = len(url_list)

    if tqdm_installed:
        for url in tqdm(url_list, desc="Downloading images", unit="img"):
            update_progress((url_list.index(url) + 1)/total_urls*100)
            download_image(script_dir,output_dir_name, url)
    else:
        for index, url in enumerate(url_list):
            default_progress_bar(index + 1, total_urls)
            download_image(script_dir, output_dir_name, url)

if __name__ == "__main__":
    main()
