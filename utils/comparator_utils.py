from PIL import Image
import imagehash
# import pymongo
import os
from datetime import datetime
import json


def get_last_modified_time(image_path):
    # Gets the image last modified date from a system file
    return datetime.utcfromtimestamp(os.path.getmtime(image_path)).isoformat() + 'Z'


def compare_images(img1Path, img2Path) -> dict:
    try:
        hash0 = imagehash.average_hash(Image.open(img1Path))
        hash1 = imagehash.average_hash(Image.open(img2Path))
        cutoff = 5  # Max number of bits that could be different in the hashes (have to experiment yet, but 5 seems ok)
        res = {
            "firstImageHash": str(hash0),
            "secondImageHash": str(hash1),
        }
        if hash0 - hash1 < cutoff:
            print(f'Images {img1Path} and {img2Path} are similar.')
            res["are_similar"] = True
        else:
            print(f'Images {img1Path} and {img2Path} are not similar.')
            res["are_similar"] = False
        return res
    except Exception as e:
        # In case of error (happened only on one file, might be a strange path name)
        return {"error": str(e)}
