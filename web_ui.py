import threading
from flask import Flask, jsonify, render_template, request, redirect, url_for
import configparser
import os
# from scraper import main, progress
from flask_socketio import SocketIO
import math 
import webbrowser
import time
import requests

# Scraper
tqdm_installed = True
try:
    from tqdm import tqdm
except:
    print("Module 'tqdm' is not installed. Using default progress indicator.")
    tqdm_installed = False
from utils.scraper_utils import *


# Starting the flask app and getting default config

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)

# Get the directory of the current script [Windows Compatibility]
script_dir = os.path.dirname(os.path.abspath(__file__))

ini_file_path = script_dir + '/appconfig.ini'


def server_is_up(url):
    """Check if the server is up by attempting to connect to it."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False
    return False

def open_browser_when_ready(url):
    """Wait for the server to start, then open the browser."""
    while not server_is_up(url):
        time.sleep(0.5)  # Check every half second
    webbrowser.open_new(url)

def startScraper(configuration: dict):
    # Get the directory of the current script [Windows Compatibility]
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ini file parsing
    # config = configparser.ConfigParser()
    # config.read(script_dir + '/appconfig.ini')

    output_dir_name = configuration.get('outputDirName')
    backward_days = 5
    subreddit_name = configuration.get("subredditName")


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
            progress = math.trunc((url_list.index(url) + 1)/total_urls*100)
            socketio.emit('update_scraper_progress', {'progress': progress})
            download_image(script_dir,output_dir_name, url)
    else:
        for index, url in enumerate(url_list):
            progress = math.trunc((url_list.index(url) + 1)/total_urls*100)
            socketio.emit('update_scraper_progress', {'progress': progress})
            default_progress_bar(index + 1, total_urls)
            
            
            download_image(script_dir, output_dir_name, url)







@socketio.on('start_scraper')
def start_scraper(data):
    formData = data
    print("current formData: " + str(formData))
    startScraper(formData)

@app.route('/')
def index():
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    settings = {
        'output_dir_name': config.get('scraper_configuration', 'output_dir_name'),
        'backward_days': config.get('scraper_configuration', 'backward_days'),
        'subreddit_name': config.get('scraper_configuration', 'subreddit_name'),
        'image_limit': config.getint('hash_comparator_config', 'image_limit')
    }
    return render_template('index.html', settings=settings)


@app.route('/comparator')
def comparator():
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    settings = {
        'output_dir_name': config.get('scraper_configuration', 'output_dir_name'),
        'backward_days': config.get('scraper_configuration', 'backward_days'),
        'subreddit_name': config.get('scraper_configuration', 'subreddit_name'),
        'image_limit': config.getint('hash_comparator_config', 'image_limit')
    }
    return render_template('comparator.html', settings=settings)

# @app.route('/start_scraper', methods=['POST'])
# def start_scraper():
#     config = configparser.ConfigParser()
#     config.read(ini_file_path)
#     config.set('scraper_configuration', 'output_dir_name', request.form['output_dir_name'])
#     config.set('scraper_configuration', 'backward_days', request.form['backward_days'])
#     config.set('hash_comparator_config', 'image_limit', request.form['image_limit'])
#     config.set('hash_comparator_config', 'base_folder', request.form['base_folder'])
#     config.set('hash_comparator_config', 'generate_json_report', request.form['generate_json_report'])
#     config.set('hash_comparator_config', 'json_report_folder', request.form['json_report_folder'])
#     config.set('hash_comparator_config', 'write_to_mongodb', request.form['write_to_mongodb'])
#     config.set('hash_comparator_config', 'mongo_connection_string', request.form['mongo_connection_string'])
#     config.set('hash_comparator_config', 'mongo_database', request.form['mongo_database'])
#     config.set('hash_comparator_config', 'mongo_collection', request.form['mongo_collection'])
#     with open(ini_file_path, 'w') as configfile:
#         config.write(configfile)
    
#     thread = threading.Thread(target=main)
#     thread.start()
#     return redirect(url_for('index'))

@app.route('/scrape_progress')
def scrape_progress():
    return jsonify({'progress': progress})

def emit_progress_scraper(progress):
    socketio.emit('update_progress_scraper', {'progress': progress})


if __name__ == '__main__':
    server_url = 'http://127.0.0.1:5000/'  # Adjust port if necessary
    threading.Thread(target=open_browser_when_ready, args=(server_url,)).start()
    app.run(debug=True, use_reloader=False)
