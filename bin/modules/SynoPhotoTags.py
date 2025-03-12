import json
from dataclasses import dataclass
from typing import List, Optional, Any, TypeVar, Generic

from pydantic import BaseModel

from bin.modules.SynoPhotos import SynoPhotos

T = TypeVar('T')
class Response(BaseModel,Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[Any] = None

class Tag(BaseModel):
    id: int
    name: str
    item_count: int = 0

class TagData(BaseModel):
    tag: Tag

class TagList(BaseModel):
    list: List[Tag]

class ErrorList(BaseModel):
    error_list: Optional[List[int]]

class SynoPhotoTags:
    SYNO_API_PHOTOS="SYNO.SynologyDrive.Photos"
    SYNO_API_PHOTOS_BROWSE_GENERAL_TAG= "SYNO.Foto.Browse.GeneralTag"
    SYNO_API_PHOTOS_BROWSE_ITEM = "SYNO.Foto.Browse.Item"
    SYNO_API_PHOTOS_BROWSE_CONDITION_ALBUM = "SYNO.Foto.Browse.ConditionAlbum"
    SYNO_API_PHOTOS_SEARCH = "SYNO.Foto.Search.Search"
    SYNO_API_PHOTOS_UPLOAD = "SYNO.Foto.Upload.Item"

    def __init__(self, server):
        self.server = server
        self.photos_api = SynoPhotos(server)

    # Removes a tag from a photo
    def remove_tag(self, tag_id, item_id_list):
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_ITEM]['path']
        request_url = self.server.host +"/webapi/" + api_path
        request_url += "?api=" + self.SYNO_API_PHOTOS_BROWSE_ITEM
        request_url += "&method=remove_tag"
        request_url += "&version=1"
        request_url += "&id=" + "["+','.join(map(str, item_id_list)) + "]"
        request_url += "&tag=" + "["+str(tag_id)+"]"
        request_url += "&SynoToken=" + self.server.session_token
        request_url += "&_sid=" + self.server.session_sid

        # '{"data":{"error_list":[]},"success":true}'
        response = self.server.client.get(request_url)


    # Removes a tag by first deleting it from all photos where it is utilized.
    # After searching all photos where it is used, finally remove the tag itself.
    def remove_tag_name(self, tag_name_to_delete):
        tag_list = self.get_tags().data.list
        item_id_list: List[int] = []
        for tag in tag_list:
            if tag.name == tag_name_to_delete:
                item_list = self.photos_api.get_items_by_tag(tag.id)
                for item in item_list:
                    item_id_list.append(item['id'])
                self.remove_tag(tag.id, item_id_list)

    # Uncomment if you want danger
    # def remove_all_tags(self):
    #     tags = self.get_tags()
    #     for tag in tags.data.list:
    #         self.remove_tag_name(tag.name)


    # Tag will get created. Save the response and ID.
    # Associate with a photo. A tag newly created needs to be added
    # to at least one photo (maybe) before it will be listed or usable as an
    # album condition.
    def create_tag(self, tag_name) -> Response[TagData]:
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_GENERAL_TAG]['path']
        request_url = self.server.host +"/webapi/" + api_path +"/SYNO.Foto.Browse.GeneralTag"

        form_data = {
            "api":self.SYNO_API_PHOTOS_BROWSE_GENERAL_TAG,
            "method":"create",
            "version":1,
            "name":'"' + tag_name + '"',
            "_sid":self.server.session_sid
        }

        headers = {
            "X-SYNO-TOKEN": self.server.session_token
        }

        #Idempotent. Will return existing id if one already exists
        # response = self.server.client.post(request_url)
        response = self.server.client.post(request_url, data=form_data, verify=False, headers=headers)

        return Response[TagData].model_validate_json(response.text)

    def add_tag(self, tag_id: int, photo_id_list: list[int]) -> Response[ErrorList]:

        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_ITEM]['path']
        request_url = self.server.host +"/webapi/" + api_path
        request_url += "?api=" + self.SYNO_API_PHOTOS_BROWSE_ITEM
        request_url += "&method=add_tag"
        request_url += "&version=1"
        request_url += "&tag=" + "["+str(tag_id)+"]"
        request_url += "&id=" + "["+','.join(map(str, photo_id_list)) + "]"
        # request_url += "&SynoToken=" + self.server.session_token
        # request_url += "&_sid=" + self.server.session_sid

        #Idempotent. Will return existing id if one already exists
        response = self.server.client.get(request_url)

        return Response[ErrorList].model_validate_json(response.text)


    def get_tags(self) -> Response[TagList] | None:
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_GENERAL_TAG]['path']
        request_url = self.server.host +"/webapi/" + api_path
        request_url += "?api=" + self.SYNO_API_PHOTOS_BROWSE_GENERAL_TAG
        request_url += "&method=list"
        request_url += "&version=1"
        request_url += "&offset=0"
        request_url += "&limit=999"
        request_url += "&SynoToken=" + self.server.session_token
        request_url += "&_sid=" + self.server.session_sid

        print("TAG LIST REQUEST: " + request_url)
        response = self.server.client.get(request_url)

        return Response[TagList].model_validate_json(response.text)
