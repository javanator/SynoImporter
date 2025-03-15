#!/usr/bin/env python
import sys
from fractions import Fraction

from src.SynoServer import SynoServer
from src.SynoPhotos import SynoPhotos
from src.Takeout import Takeout
import os
import piexif
import json
from pathlib import Path
from PIL import Image, ExifTags
import io
from src import ExifUtil
from src.SynoPhotoTags import SynoPhotoTags
from src.Takeout import PhotoMetadata, AlbumMetadata

HOST = "https://" + os.path.join(sys.argv[1])
USERNAME = sys.argv[2]
PASSWORD = sys.argv[3]
INPUTPATH = sys.argv[4]

server = SynoServer(HOST)
server.login(USERNAME, PASSWORD)
photo_api = SynoPhotos(server)
tag_api = SynoPhotoTags(server)

def traverse_directory(directory, file_lambda, dir_lambda):
    try:
        entries = os.listdir(directory)
        for entry in entries:
            # Join the current directory path with the entry name
            full_path = os.path.join(directory, entry)

            # Check if the entry is a directory or a file
            if os.path.isdir(full_path):
                dir_lambda(full_path)
                traverse_directory(full_path, file_lambda,dir_lambda)
            if os.path.isfile(full_path):
                file_lambda(full_path)
    except Exception as e:
        print(f"Error reading directory {directory}: {e}")

def on_dir(dir_path):
    metadata_file = os.path.join(dir_path, "metadata.json")
    if Path(metadata_file).exists():
        print("metadata.json file exists. This is a photo album.")

        # Open the file and load its contents
        with open(metadata_file, 'r', encoding='utf-8') as file:
            # Create a Metadata object from the JSON contents
            album_metadata = AlbumMetadata.model_validate_json(file.read())

            #Check if album exists. Create a new one if not.
            #album_list = photo_api.album_list()
            #existing_album = photo_api.get_album_by_name(album_list.data.list, album_metadata.title)

            #if existing_album is None:
                #tag_response = tag_api.create_tag(album_metadata.title)
                #photo_api.create_tag_album(album_metadata.title, tag_response.data.tag.id)


def on_file(file_path: str):
    if Path(file_path).suffix == ".json" and file_path.endswith("metadata.json") == False:

        with open(file_path, 'r', encoding='utf-8') as f:
            photo_metadata = PhotoMetadata.model_validate_json(f.read())
            exif_data = Takeout.read_google_takeout_json(photo_metadata)
            image_file = os.path.dirname(file_path) + "/" + photo_metadata.title
            image = Image.open(image_file)
            file_type = image.format
            image = ExifUtil.merge_exif_data(image._getexif(), exif_data)
            print(file_path)
            print(exif_data)








# Open and parse the JSON file
# photo_json = None
# with open("./sample/20220405_104404.jpg.json", 'r', encoding='utf-8') as f:
#     photo_json = json.load(f)
# exif_data_supplement = Takeout.read_google_takeout_json(photo_json)
#
# image_file = photo_json['title']
# image_file = "./sample/" + image_file
# image = Image.open(image_file)
#
# new_exif = ExifUtil.merge_exif_data(ExifUtil.load_exif_data(image), exif_data_supplement)
# exif_bytes = piexif.dump(new_exif)
# with io.BytesIO() as output_stream:
#     image.save(output_stream, format="jpeg", exif=exif_bytes)
#     output_stream.seek(0)
#
#     # JPEG file with EXIF data has been created. Now Upload to Server
#     with open("./sample/test.jpg", "wb") as output_file:
#         output_file.write(output_stream.read())

# traverse_directory(INPUTPATH, on_file, on_dir)
on_file("samples/Takeout/Barbie 🩷/20220212_112850.jpg.json")

server.logout()


