import time
import json
import requests
import shutil
import glob
import instaloader
import os
from pathlib import Path

print('Starting monitoring tool')

dirpath = os.getcwd()
foldername = os.path.basename(dirpath)

HOME_DIR = dirpath

APP_PATH_ROOT = HOME_DIR
APP_SCRIPT_PATH = APP_PATH_ROOT
HASHTAG = 'streetart'
INSTAGRAM_USER_NAME = 'streetarrrrt'
INSTAGRAM_USER_PAME = 'password123!'
INSTAGRAM_INDEX_HASHTAG = HASHTAG
IS_PROD = True

print(APP_PATH_ROOT)

previously_completed_art_name = ''

PROD_URL = 'https://www.publicart.io'
STAG_URL = 'https://publicart-site-staging.herokuapp.com'
ROOT_URL = PROD_URL if IS_PROD else STAG_URL
IMAGE_ROOT_PATH = './#' + HASHTAG + '/'
LOCATION_POST_FIX = '_location.txt'
JPG_POST_FIX = '.jpg'
LOCATION_UTC_POST_FIX = '_UTC' + LOCATION_POST_FIX
API_URL = ROOT_URL + '/pictures?no_partial=1'
METADATA_URL = ROOT_URL + '/pictures/metadata'
GENERIC_HEADER = {'Content-type': 'multipart/form-data'}
GOOGLE_MAPS_URL_BASE = 'https://maps.google.com/maps?q='
TRANSFERED_ART_DIR = 'transfered_' + HASHTAG
DEFAULT_ART_DIR = '#' + HASHTAG


def delete_folder(media_id):
    shutil.rmtree(APP_PATH_ROOT + '/images/' + str(media_id))
    print('Deleted ' + str(media_id))


def after_submit_image_get_id(r):
    json_data = json.loads(r.text)
    picture_id = json_data['picture_id']
    return picture_id


def get_date_from_name(date):
    return date.strftime("%m-%d-%Y_%H-%M-%S")


def generate_metadata(picture_id, data):
    r = requests.post(METADATA_URL, data=data)


def upload_file_to_publicart(media_id, file_path, date_of_image, location):
    files = {'file': open(file_path, 'rb')}
    file_response = requests.post(API_URL, files=files)
    print('response ', file_response)
    if file_response.ok:
        print('success ', file_path)
        picture_id = after_submit_image_get_id(file_response)
        print('picture_id ', str(picture_id))

        # data = {"location_name": location_name, "file_name": art_name, "latitude": latlon[0], "longitude": latlon[1]}
        data = {"date_of_image": date_of_image, "location_name": location.name, "file_name": media_id,
                "latitude": location.lat, "longitude": location.lng, "picture_id": picture_id}
        generate_metadata(picture_id, data)
    else:
        print('issue ', file_path)
        time.sleep(15)
        upload_file_to_publicart(file_path)


def submit_image_and_get_id(media_id, date, location):
    art_piece_images = glob.glob(HOME_DIR + '/images/' + str(media_id) + '/*.jpg')
    date_of_image = get_date_from_name(date)

    length = len(art_piece_images)
    print('Images total ' + str(length))
    for i in range(length):
        print('Uploading ' + str(i))
        file_path = art_piece_images[i]
        print(art_piece_images[i])
        upload_file_to_publicart(media_id, file_path, date_of_image, location)

    delete_folder(media_id)


def index_images():
    L = instaloader.Instaloader(download_videos=False, compress_json=False)
    L.login(INSTAGRAM_USER_NAME, INSTAGRAM_USER_PAME)
    print('Indexing started')
    for post in L.get_hashtag_posts(HASHTAG):
        # post is an instance of instaloader.Post
        if post.location is not None:
            was_downloaded = L.download_post(post, target=Path('images/', str(post.mediaid)))
            submit_image_and_get_id(post.mediaid, post.date, post.location)


index_images()
