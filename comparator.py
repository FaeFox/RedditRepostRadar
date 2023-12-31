from PIL import Image
import imagehash
import pymongo
import os
from datetime import datetime
import json
# This is my mini pc, I have it in the path because it's on a shared folder I access from my main PC
from utils.comparator_utils import *
import configparser
# ini file parsing 

config = configparser.ConfigParser()
config.read('appconfig.ini', encoding="utf8")

base_folder = config.get('hash_comparator_config', 'base_folder')
generate_json_report = config.getboolean('hash_comparator_config', 'generate_json_report')
write_to_mongodb= config.getboolean('hash_comparator_config', 'write_to_mongodb')
mongo_connection_string = config.get('hash_comparator_config', 'mongo_connection_string')
mongo_database = config.get('hash_comparator_config', 'mongo_database')
mongo_collection = config.get('hash_comparator_config', 'mongo_collection')
json_report_folder =config.get('hash_comparator_config', 'json_report_folder')
image_limit =config.getint('hash_comparator_config', 'image_limit')

report_list = []



def traverse_folder(folder_path, previous_image_path=None, limit=100):
    # Ignore formats list
    ignore_formats = ['.gif', '.mp4', '.avi', '.mov']

    # Counter of compared images
    image_count = 0
   

    # Scan file in folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Ignore other formats (for now?)
        if any(file_name.lower().endswith(fmt) for fmt in ignore_formats):
            continue

        # If it's a folder, recall the function
        if os.path.isdir(file_path):
            traverse_folder(file_path, previous_image_path, limit)
        else:
            # if it's an image, compare it with the previous
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                current_image_path = file_path
                if previous_image_path is not None:
                    are_similar_res = compare_images(previous_image_path, current_image_path)
                    if "error" in are_similar_res:
                        print(f"Error comparing images {previous_image_path} and {current_image_path}: {are_similar_res['error']}")
                        continue
                    are_similar = are_similar_res.get("are_similar")
                    firstImageHash = are_similar_res.get("firstImageHash")
                    secondImageHash = are_similar_res.get("secondImageHash")
                    last_modified_image1 = get_last_modified_time(previous_image_path)
                    last_modified_image2 = get_last_modified_time(current_image_path)
                    
                    # Write element as json item
                    report_list.append({
                    "comparison": {
                        "firstImage": {
                            "path": previous_image_path,
                            "last_modified": last_modified_image1,
                            "hash": firstImageHash
                        },
                        "secondImage": {
                            "path": current_image_path,
                            "last_modified": last_modified_image2,
                            "hash": secondImageHash
                        },
                        "are_similar": are_similar
                    }
                })

                # For next iteration
                previous_image_path = current_image_path

              
                image_count += 1

                # check the limit, if 0 download all
                if limit > 0 and image_count >= limit:
                    break


traverse_folder(base_folder, limit=image_limit)

# Report generation
report_data = {
            "report": report_list,
}


if generate_json_report:
    with open(json_report_folder+"/"+ 'report.json', 'w') as json_file:
            json.dump(report_data, json_file, indent=2)

if write_to_mongodb:
    print("Writing to MongoDB... "+ mongo_connection_string)
    client = pymongo.MongoClient(mongo_connection_string)
    db = client[mongo_database]
    print("Writing to db...")
    collection = db[mongo_collection]
    print("Writing to collection...")
    for item in report_list:
        collection.insert_one(item)
    print("Written to MongoDB successfully...")
