#!/usr/bin/env python
import os
import sys
import tempfile

from PIL import Image
from pathlib import Path
from pyexiv2 import ImageMetadata

from src import Filesystem
from src.SynoPhotoTags import SynoPhotoTags
from src.SynoPhotos import SynoPhotos
from src.SynoServer import SynoServer
from src.Takeout import TakeoutPhotoMetadata, AlbumMetadata, TakeoutPhotoDescriptor


def on_dir(dir_path):
    metadata_file = os.path.join(dir_path, "metadata.json")
    if Path(metadata_file).exists():
        # Open the file and load its contents
        with open(metadata_file, 'r', encoding='utf-8') as file:
            # Create a Metadata object from the JSON contents
            album_metadata = AlbumMetadata.model_validate_json(file.read())
            print(f"Importing album {album_metadata.title}")


def on_file(file_path: str):
    if Path(file_path).suffix == ".json" and file_path.endswith("metadata.json") == False:
        with (open(file_path, 'r', encoding='utf-8') as f):
            takeout_photo_metadata = TakeoutPhotoMetadata.model_validate_json(f.read())
            takeout_image_filename = os.path.dirname(file_path) + "/" + takeout_photo_metadata.title

            with Image.open(os.fsdecode(
                    takeout_image_filename)) as original_image, tempfile.NamedTemporaryFile() as temporary_image:
                original_image.save(temporary_image.name, format=original_image.format)
                original_image_metadata = ImageMetadata(os.fspath(takeout_image_filename))
                original_image_metadata.read()

                temp_image_metadata = ImageMetadata(temporary_image.name)
                temp_image_metadata.read()

                original_image_metadata.copy(temp_image_metadata)
                photo_descriptor = TakeoutPhotoDescriptor(takeout_photo_metadata)
                photo_descriptor.set_exif_gps(temp_image_metadata)
                temp_image_metadata.write()

                print(f"Importing from temp file {temporary_image.name} image {original_image.filename}")


if __name__ == "__main__":
    HOST = "https://" + os.path.join(sys.argv[1])
    USERNAME = sys.argv[2]
    PASSWORD = sys.argv[3]
    INPUTPATH = sys.argv[4]

    server = SynoServer(HOST)
    server.login(USERNAME, PASSWORD)
    photo_api = SynoPhotos(server)
    tag_api = SynoPhotoTags(server)
    Filesystem.traverse_directory(INPUTPATH, on_file, on_dir)
    server.logout()
