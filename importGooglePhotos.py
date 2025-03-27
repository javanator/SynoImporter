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

def add_synology_tag(image_metadata: ImageMetadata, tag: str):
    """
    This function adds a synology photos tag directly to image metadata. The purpose is to avoid round trip service
    calls with the synology API by adding the tags directly to the image metadata.
    :param image_metadata:
    :param tag:
    :return:
    """
    if "Xmp.dc.subject" in image_metadata.keys():
        image_metadata["Xmp.dc.subject"].append(tag)
    else:
        image_metadata["Xmp.dc.subject"]=[tag]

    if "Iptc.Application2.Keywords" in image_metadata.keys():
        image_metadata["Iptc.Application2.Keywords"].append(tag)
    else:
        image_metadata["Iptc.Application2.Keywords"]=[tag]

def tagify(text: str) -> str:
    tag_name = text.encode('ascii', 'ignore').decode().strip()
    tag_name = tag_name.lower().replace(" ", "_").rstrip("_")
    tag_name = "tag_"+tag_name

    return tag_name

def on_dir(dir_path):
    metadata_file = os.path.join(dir_path, "metadata.json")
    if Path(metadata_file).exists():
        # Open the file and load its contents
        with open(metadata_file, 'r', encoding='utf-8') as file:
            # Create a Metadata object from the JSON contents
            album_metadata = AlbumMetadata.model_validate_json(file.read())
            album_tag_name = tagify(album_metadata.title)
            album_tag = tag_api.create_tag(tag_name=album_tag_name)
            # create_album_response = photo_api.create_tag_album(album_name=album_tag_name,tag_id=album_tag.data.tag.id)
            print(f"Importing album {album_metadata.title}")


def on_file(file_path: str):
    if Path(file_path).suffix == ".json" and file_path.endswith("metadata.json") == False:
        with (open(file_path, 'r', encoding='utf-8') as f):
            takeout_photo_metadata = TakeoutPhotoMetadata.model_validate_json(f.read())
            takeout_image_filename = os.path.dirname(file_path) + "/" + takeout_photo_metadata.title
            takeout_album = os.path.basename(os.path.dirname(takeout_image_filename)).replace(" ", "_")
            takeout_album_tag = tagify(takeout_album)
            with Image.open(os.fsdecode(
                    takeout_image_filename)) as original_image, tempfile.NamedTemporaryFile() as temporary_image:
                original_image.save(temporary_image.name, format=original_image.format)
                original_image_metadata = ImageMetadata(os.fspath(takeout_image_filename))
                original_image_metadata.read()

                temp_image_metadata = ImageMetadata(temporary_image.name)
                temp_image_metadata.read()
                add_synology_tag(temp_image_metadata, takeout_album_tag)

                original_image_metadata.copy(temp_image_metadata)
                photo_descriptor = TakeoutPhotoDescriptor(takeout_photo_metadata)
                photo_descriptor.set_exif_gps(temp_image_metadata)

                temp_image_metadata.write()

                #Upload the image
                uploaded_photo_response = photo_api.photo_upload(temporary_image.read(), takeout_photo_metadata.title)

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

    #This needs to be a depth-first search. Images need to be tagged FIRST in order to create a tag based album
    Filesystem.traverse_directory(INPUTPATH, on_file, on_dir)
    server.logout()
