import threading
from flask import Flask, jsonify, render_template, request, redirect, url_for
import configparser
import os
from scraper import main, progress

app = Flask(__name__, static_folder='static')


# Get the directory of the current script [Windows Compatibility]
script_dir = os.path.dirname(os.path.abspath(__file__))

ini_file_path = script_dir + '/appconfig.ini'

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

@app.route('/start_scraper', methods=['POST'])
def start_scraper():
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    config.set('scraper_configuration', 'output_dir_name', request.form['output_dir_name'])
    config.set('scraper_configuration', 'backward_days', request.form['backward_days'])
    config.set('hash_comparator_config', 'image_limit', request.form['image_limit'])
    config.set('hash_comparator_config', 'base_folder', request.form['base_folder'])
    config.set('hash_comparator_config', 'generate_json_report', request.form['generate_json_report'])
    config.set('hash_comparator_config', 'json_report_folder', request.form['json_report_folder'])
    config.set('hash_comparator_config', 'write_to_mongodb', request.form['write_to_mongodb'])
    config.set('hash_comparator_config', 'mongo_connection_string', request.form['mongo_connection_string'])
    config.set('hash_comparator_config', 'mongo_database', request.form['mongo_database'])
    config.set('hash_comparator_config', 'mongo_collection', request.form['mongo_collection'])
    with open(ini_file_path, 'w') as configfile:
        config.write(configfile)
    
    thread = threading.Thread(target=main)
    thread.start()
    return redirect(url_for('index'))

@app.route('/scrape_progress')
def scrape_progress():
    return jsonify({'progress': progress})

if __name__ == '__main__':
    app.run(debug=True)
