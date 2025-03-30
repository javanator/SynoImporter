#!/usr/bin/env python
import logging
import os
import sys
import tempfile
from unittest import case

from PIL import Image
from pathlib import Path
from pyexiv2 import ImageMetadata
from magic import Magic
from pillow_heif import register_heif_opener

from src.SynoPhotoTags import SynoPhotoTags
from src.SynoPhotos import SynoPhotos,ActionData, Response
from src.SynoServer import SynoServer
from src.Takeout import TakeoutPhotoMetadata, AlbumMetadata, TakeoutPhotoDescriptor

def add_synology_tag(image_metadata: ImageMetadata, tag: str):
    """
    This mechanism does not seem to work, despite anecdotal reports.
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
    tag_name = "album_"+tag_name

    return tag_name

def on_dir(dir_path :str, files_results: [Response[ActionData]]):
    metadata_file = Path(dir_path).joinpath( "metadata.json")
    if Path(metadata_file).exists():
        # Open the file and load its contents
        with open(metadata_file, 'r', encoding='utf-8') as file:
            # Create a Metadata object from the JSON contents
            album_metadata = AlbumMetadata.model_validate_json(file.read())
            album_tag_name = tagify(album_metadata.title)
            album_tag = tag_api.create_tag(tag_name=album_tag_name)
            id_list = list(map(lambda response: response.data.id if response.success and response.data else None, files_results))
            tag_photos_response = tag_api.add_tag(album_tag.data.tag.id, id_list)
            albums_response_list=photo_api.album_list()
            existing_album = photo_api.get_album_by_name(albums_response_list.data.list, album_metadata.title)
            if not existing_album:
                create_album_response = photo_api.create_tag_album(album_name=album_metadata.title,tag_id=album_tag.data.tag.id)
                print(f"Imported album {album_metadata.title}")


def on_file(file_path: str) -> ActionData | None:
    excluded_files = ['metadata.json', 'print-subscriptions.json','shared_album_comments.json',
                      'user-generated-memory-titles.json','metadata(1).json']
    if Path(file_path).suffix == ".json" and not Path(file_path).name in excluded_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            takeout_file_metadata = TakeoutPhotoMetadata.model_validate_json(f.read())
            takeout_file_filename = os.path.dirname(file_path) + "/" + takeout_file_metadata.title

            match file_type := check_file_type(takeout_file_filename):
                case 'image':
                    return import_image(takeout_file_filename, takeout_file_metadata)
                case 'video':
                    return import_video(takeout_file_filename, takeout_file_metadata)
    return None

def check_file_type(file_path):
    mime = Magic(mime=True)
    file_type = mime.from_file(file_path)
    if file_type.startswith('image/'):
        return 'image'
    elif file_type.startswith('video/'):
        return 'video'
    return 'other'

def import_video(takeout_video_filename, takeout_video_metadata) -> ActionData | None:
    takeout_album = os.path.basename(os.path.dirname(takeout_video_filename)).replace(" ", "_")
    takeout_album_tag = tagify(takeout_album)

    #No need to manipulate. Just upload
    with open(os.fsdecode(takeout_video_filename),'rb') as video_file:
        uploaded_movie_response = photo_api.photo_upload(image_bytes = video_file.read(), name = takeout_video_metadata.title)
        print(f"Imported video {takeout_video_filename}")
        return uploaded_movie_response


def import_image(takeout_image_filename, takeout_photo_metadata) -> ActionData | None:
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

        # Upload the image
        uploaded_photo_response = photo_api.photo_upload(temporary_image.read(), takeout_photo_metadata.title)

        print(f"Importing from temp file {temporary_image.name} image {original_image.filename}")
        return uploaded_photo_response


def traverse_directory(directory: str, file_lambda, dir_lambda) -> [ActionData]:
        entries = os.listdir(directory)
        results :[ActionData] = []
        for entry in entries:
            # Join the current directory path with the entry name
            full_path = directory + "/" + entry

            # Check if the entry is a directory or a file
            if os.path.isdir(full_path):
                recursed_result = traverse_directory(full_path, file_lambda,dir_lambda)
                #Keeping this here for depth-first traversal
                dir_lambda(full_path, recursed_result)
            else:
                result = file_lambda(full_path)
                if result is not None:
                    results.append(result)

        return results

if __name__ == "__main__":
    HOST = "https://" + os.path.join(sys.argv[1])
    USERNAME = sys.argv[2]
    PASSWORD = sys.argv[3]
    INPUTPATH = sys.argv[4]

    register_heif_opener()

    server = SynoServer(HOST)
    server.login(USERNAME, PASSWORD)
    photo_api = SynoPhotos(server)
    tag_api = SynoPhotoTags(server)

    # logging.getLogger("requests").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    # logging.getLogger("http.client").setLevel(logging.WARNING)

    #This needs to be a depth-first search. Images need to be tagged FIRST in order to create a tag based album
    traverse_directory(INPUTPATH, on_file, on_dir)
    server.logout()
