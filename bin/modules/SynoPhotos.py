import json
import mimetypes
import os

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypeVar, Generic
from datetime import datetime
from pydantic.dataclasses import dataclass

T = TypeVar('T')
class ErrorDetails(BaseModel):
    code: int

class Response(BaseModel,Generic[T]):
    data: Optional[T] = None
    success: bool
    error: Optional[ErrorDetails] = None

class Owner(BaseModel):
    id: int
    name: str

class SharingInfo(BaseModel):
    enable_password: bool
    expiration: int
    is_expired: bool
    mtime: int
    owner: Owner
    passphrase: str
    permission: List[Any]
    privacy_type: str
    sharing_link: str
    type: str

class Thumbnail(BaseModel):
    cache_key: str
    m: str
    preview: str
    sm: str
    unit_id: int
    xl: str

class Additional(BaseModel):
    sharing_info: SharingInfo
    thumbnail: Thumbnail

class Album(BaseModel):
    additional: Optional[Additional] = None
    cant_migrate_condition: Optional[Dict[str, Any]] = Field(default={})
    condition: Dict[str, Any]
    create_time: int
    end_time: int
    freeze_album: Optional[bool] = Field(default=False)
    id: int
    item_count: int
    name: str
    owner_user_id: int
    passphrase: str
    shared: bool
    sort_by: str
    sort_direction: str
    start_time: int
    temporary_shared: Optional[bool] = Field(default=False)
    type: str
    version: int

class AlbumList(BaseModel):
    list: List[Album]

class AlbumData(BaseModel):
    album: Album

class SynoPhotos:
    SYNO_API_PHOTOS="SYNO.SynologyDrive.Photos"
    SYNO_API_PHOTOS_BROWSE_GENERAL_TAG= "SYNO.Foto.Browse.GeneralTag"
    SYNO_API_PHOTOS_BROWSE_ITEM = "SYNO.Foto.Browse.Item"
    SYNO_API_PHOTOS_BROWSE_CONDITION_ALBUM = "SYNO.Foto.Browse.ConditionAlbum"
    SYNO_API_PHOTOS_BROWSE_NORMAL_ALBUM = "SYNO.Foto.Browse.NormalAlbum"
    SYNO_API_PHOTOS_SEARCH = "SYNO.Foto.Search.Search"
    SYNO_API_PHOTOS_UPLOAD = "SYNO.Foto.Upload.Item"

    def __init__(self, server):
        self.server = server
        self.current_id=None
        self.current_id=self.get_userinfo()['data']['id']

    def get_album_by_name(album_list: list, name: str) -> Album | None:
        """
        Retrieve a single album from the list of albums using the name as the key.
        """
        for album_data in album_list:
            if album_data.get("name") == name:
                return Album.from_dict(album_data)
    def album_list(self)-> Response[AlbumList]:
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS]['path']
        request_url = self.server.host +"/webapi/" + api_path

        params={
            "method":"list",
            "version": str(4),
            "api":"SYNO.Foto.Browse.Album",
            "offset":str(0),
            "limit":"999"
        }

        syno_photos_response = self.server.client.get(request_url, params=params)

        return Response[AlbumList].model_validate_json(syno_photos_response.text)

    def album_remove_by_name(self, album_name) -> Response | None:
        album_list_response = self.album_list()
        for album in album_list_response.data.list:
            if album_name == album.name:
                #There might be multiple by the same name
                self.album_remove_by_id(album.id)

        return Response(
            success=True,
            data=None,
            error=None)

    def album_remove_by_id(self, album_id) -> Response:
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS]['path']
        url = self.server.host +"/webapi/" + api_path

        params={
            "method":"delete",
            "version": str(1),
            "api":"SYNO.Foto.Browse.Album",
            "id": '[' + str(album_id) + ']'
        }

        response = self.server.client.get(url, params=params)

        return Response.model_validate_json(response.text)

    def create_tag_album(self, album_name, tag_id) -> Response[AlbumData] | None :
        json_data = json.loads('{"user_id":0,"item_type":[],"general_tag":[],"general_tag_policy":"or"}')
        json_data['general_tag'].append(tag_id)
        json_data['user_id']=self.current_id

        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_CONDITION_ALBUM]['path']
        url = self.server.host +"/webapi/" + api_path

        form_data = {
            "api":"SYNO.Foto.Browse.ConditionAlbum",
            "method":"create",
            "version":3,
            "name":'"' + album_name + '"',
            "condition":json.dumps(json_data),
            "_sid":self.server.session_sid
        }

        headers = {
            "X-SYNO-TOKEN": self.server.session_token
        }

        response = self.server.client.post(url, data=form_data, verify=False, headers={"X-SYNO-TOKEN":self.server.session_token})
        response_object = Response[AlbumData].model_validate_json(response.text)

        return response_object

    def create_normal_album(self, album_name: str,album_items: list[int]) -> Response[AlbumData] | None :

        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_NORMAL_ALBUM]['path']
        url = self.server.host +"/webapi/" + api_path

        form_data = {
            "api":self.SYNO_API_PHOTOS_BROWSE_NORMAL_ALBUM,
            "method":"create",
            "version":1,
            "name": "" + album_name + "",
            "item":str(album_items),
            "_sid":self.server.session_sid
        }

        headers = {
            "X-SYNO-TOKEN": self.server.session_token
        }

        response = self.server.client.post(url, data=form_data, verify=False, headers={"X-SYNO-TOKEN":self.server.session_token})
        response_object = Response[AlbumData].model_validate_json(response.text)

        return response_object


    def get_userinfo(self):
        SYNO_FOTO_USERINFO = "SYNO.Foto.UserInfo"
        auth_path = self.server.apiInfo['data'][SYNO_FOTO_USERINFO]['path']
        request_url= self.server.host + "/webapi/" + auth_path

        params={
            "api":SYNO_FOTO_USERINFO,
            "version":str(1),
            "method":"me",
            "enable_syno_token":"yes",
            "format":"cookie"
        }

        response = self.server.client.get(request_url, params=params)
        return response.json()

    def get_items_by_tag(self, tag_id):
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_BROWSE_ITEM]['path']
        request_url = self.server.host +"/webapi/" + api_path
        request_url += "?api=" + self.SYNO_API_PHOTOS_BROWSE_ITEM
        request_url += "&method=list"
        request_url += "&version=4"
        request_url += "&offset=0"
        request_url += "&limit=999"
        request_url += "&general_tag_id=" + str(tag_id)
        request_url += "&SynoToken=" + self.server.session_token
        request_url += "&_sid=" + self.server.session_sid

        print("ITEM BY TAG REQUEST: " + request_url)
        response = self.server.client.get(request_url)
        print(response.json())

        return response.json()['data']['list']



    def photo_search(self, keyword):
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_SEARCH]['path']
        url = self.server.host +"/webapi/" + api_path
        params = {
            "api":self.SYNO_API_PHOTOS_SEARCH,
            "method":"list_item",
            "version":str(1),
            "offset":str(0),
            "limit":"100",
            "additional":'["thumbnail","resolution","orientation","video_convert","video_meta","address"]',
            "keyword":'"'+keyword+"'"
        }

        response = self.server.client.get(url, params=params)
        return response.json()['data']['list']

    def photo_match(self, **kwargs):
        filename = kwargs.get("filename", None)
        filesize = kwargs.get("filesize", None)

        results = self.photo_search(filename)

        for result in results:
            if filename == result['filename']:
                if filesize is not None and filesize == result['filesize']:
                    return result
                if filesize is None:
                    return result

        return None

    def photo_upload(self, filepath):
        api_path = self.server.apiInfo['data'][self.SYNO_API_PHOTOS_UPLOAD]['path']
        url = self.server.host +"/webapi/" + api_path

        mimetype = mimetypes.guess_type(filepath)
        filename = os.path.basename(filepath)
        params = {
            "api":self.SYNO_API_PHOTOS_UPLOAD,
            "method":"upload_to_folder",
            "version":str(1),
            "target_folder_id":str(3),
            "duplicate" : '"ignore"',
            "name":'"'+filename+'"',
            # "mtime":  Date.now().getTime()
        }
        image = None
        with open(filepath, "rb") as f:
            image = f.read()

        files = {
            "file": (filename, image, mimetype),
        }

        headers = {
            "X-SYNO-TOKEN": self.server.session_token
        }

        response = self.server.client.post(url, data=params, headers=headers, files=files, verify=False)

        print(response.json())