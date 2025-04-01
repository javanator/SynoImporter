"""
This file is also AI garbage. Clean it up later
TODO: Add typing for awesomeness

"""

import json
from fractions import Fraction
from typing import Optional, Dict, Any

import pyexiv2
from pydantic import BaseModel
from datetime import datetime
from pyexiv2 import ImageMetadata
from src import ExifUtil
from exif import GpsAltitudeRef

class TimeInfo(BaseModel):
    timestamp: str
    formatted: str

    def get_datetime(self) -> datetime:
        """Convert timestamp to datetime object"""
        return datetime.fromtimestamp(int(self.timestamp))
class AlbumComment(BaseModel):
    text: Optional[str]
    creationTime: Optional[TimeInfo]

class AlbumMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    access: Optional[str] = None
    date: Optional[TimeInfo] = None
    contentOwnerName: Optional[str] = None
    sharedAlbumComments: Optional[list[AlbumComment]] = None

class GeoData(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    latitudeSpan: float
    longitudeSpan: float

class DeviceFolder(BaseModel):
    localFolderName: str

class MobileUpload(BaseModel):
    deviceFolder: Optional[DeviceFolder] = None
    deviceType: str

class ThirdPartyApp(BaseModel):
    appName: str

class GooglePhotosOrigin(BaseModel):
    mobileUpload: Optional[MobileUpload] = None
    thirdPartyApp: Optional[ThirdPartyApp] = None

class TakeoutPhotoMetadata(BaseModel):
    title: str
    description: str
    imageViews: str
    access: Optional[str] = None
    date: Optional[TimeInfo] = None
    creationTime: Optional[TimeInfo] = None
    photoTakenTime: Optional[TimeInfo] = None
    geoData: GeoData
    geoDataExif: Optional[GeoData] = None
    url: str
    googlePhotosOrigin: GooglePhotosOrigin



class TakeoutPhotoDescriptor:
    # See https://exiv2.org/tags.html for tag names
    # DateTime Format is YYYY:MM:DD HH:MM:SS
    def __init__(self, takeout_photo_metadata: TakeoutPhotoMetadata):
        self.takeout_photo_metadata: TakeoutPhotoMetadata = takeout_photo_metadata

    def set_exif_gps(self, image_metadata: ImageMetadata):

        # Set GPS fields from takeout metadata to the image
        if self.takeout_photo_metadata.geoDataExif:
            gps_data = self.takeout_photo_metadata.geoDataExif

            if gps_data.latitude:
                latitude = float(gps_data.latitude)
                latitude_dms = ExifUtil.deg_to_dms(latitude,["S", "N"])
                image_metadata['Exif.GPSInfo.GPSLatitudeRef'] = [latitude_dms[3]]
                image_metadata['Exif.GPSInfo.GPSLatitude'] = [latitude_dms[0],latitude_dms[1],latitude_dms[2]]
            if gps_data.longitude:
                longitude = float(gps_data.longitude)
                longitude_dms = ExifUtil.deg_to_dms(longitude, ["W", "E"])
                image_metadata['Exif.GPSInfo.GPSLongitudeRef'] = [longitude_dms[3]]
                image_metadata['Exif.GPSInfo.GPSLongitude'] = [longitude_dms[0],longitude_dms[1],longitude_dms[2]]
            if gps_data.altitude:
                image_metadata['Exif.GPSInfo.GPSAltitude'] = Fraction(gps_data.altitude).limit_denominator(1)
                image_metadata['Exif.GPSInfo.GPSAltitudeRef'] = '0' #1 if below sea level

    def set_exif_date_time(self, temp_image_metadata :ImageMetadata):
        if self.takeout_photo_metadata.creationTime:
            creation_time = self.takeout_photo_metadata.creationTime.get_datetime()
            temp_image_metadata['Exif.Photo.DateTimeDigitized'] = creation_time.strftime("%Y:%m:%d %H:%M:%S")
        if self.takeout_photo_metadata.photoTakenTime:
            taken_time = self.takeout_photo_metadata.photoTakenTime.get_datetime()
            temp_image_metadata['Exif.Image.DateTime'] = taken_time.strftime("%Y:%m:%d %H:%M:%S")
            temp_image_metadata['Exif.Photo.DateTimeOriginal'] = taken_time.strftime("%Y:%m:%d %H:%M:%S")
        pass