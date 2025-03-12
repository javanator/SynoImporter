#!/usr/bin/env python
import os
import sys

from bin.modules.SynoPhotoTags import SynoPhotoTags
from bin.modules.SynoServer import SynoServer
from bin.modules.SynoPhotos import SynoPhotos

HOST = "https://" + os.path.join(sys.argv[1])
USERNAME = sys.argv[2]
PASSWORD = sys.argv[3]

server = SynoServer(HOST)
server.login(USERNAME, PASSWORD)

photos_api = SynoPhotos(server)
tag_api = SynoPhotoTags(server)


# all_tags = tag_api.get_tags()
# tag_response = tag_api.create_tag("tag_test02")

#photos_api.album_remove_by_name("test_album02")
#photos_api.album_remove_by_name("testalbum01")


# addtag_response = tag_api.add_tag(tag_id=tag_response.data.tag.id,photo_id_list=[3596])
# album_create_response = photos_api.create_normal_album("test_album02", [104263])
album_remove_response = photos_api.album_remove_by_name(album_name="test_album02")

# album_remove_response = photos_api.album_remove_by_id(1196)
# albums = photos_api.album_list()
exit(0)