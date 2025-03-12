#!/usr/bin/env python
import os
import sys
from bin.modules.SynoServer import SynoServer
from bin.modules.SynoPhotoTags import SynoPhotoTags
from bin.modules.SynoPhotos import SynoPhotos

HOST = "https://" + os.path.join(sys.argv[1])
USERNAME = sys.argv[2]
PASSWORD = sys.argv[3]

server = SynoServer(HOST)
server.login(USERNAME, PASSWORD)

tags_api = SynoPhotoTags(server)
photos_api = SynoPhotos(server)
response = photos_api.album_list()

print(response)
