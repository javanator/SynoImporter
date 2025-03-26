"""
This file is also AI garbage. Clean it up later
TODO: Add typing for awesomeness

"""

import json
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from pyexiv2 import ImageMetadata
from src import ExifUtil

class DateInfo(BaseModel):
    timestamp: str
    formatted: str

    def to_datetime(self) -> datetime:
        """Convert the timestamp to a Python datetime object."""
        return datetime.fromtimestamp(int(self.timestamp))

class AlbumMetadata(BaseModel):
    title: str
    description: Optional[str] = ""
    access: str
    date: DateInfo

class TimeInfo(BaseModel):
    timestamp: str
    formatted: str

    def get_datetime(self) -> datetime:
        """Convert timestamp to datetime object"""
        return datetime.fromtimestamp(int(self.timestamp))

class GeoData(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    latitudeSpan: float
    longitudeSpan: float

class DeviceFolder(BaseModel):
    localFolderName: str

class MobileUpload(BaseModel):
    deviceFolder: DeviceFolder
    deviceType: str

class GooglePhotosOrigin(BaseModel):
    mobileUpload: MobileUpload

class TakeoutPhotoMetadata(BaseModel):
    title: str
    description: str
    imageViews: str
    creationTime: TimeInfo
    photoTakenTime: TimeInfo
    geoData: GeoData
    geoDataExif: GeoData
    url: str
    googlePhotosOrigin: GooglePhotosOrigin



class TakeoutPhotoDescriptor:
    def __init__(self, takeout_photo_metadata: TakeoutPhotoMetadata):
        self.takeout_photo_metadata: TakeoutPhotoMetadata = takeout_photo_metadata

    def set_exif_gps(self, image_metadata: ImageMetadata):

        # Set GPS fields from takeout metadata to the image
        if self.takeout_photo_metadata.geoDataExif:
            gps_data = self.takeout_photo_metadata.geoDataExif

            if gps_data.latitude:
                latitude = float(gps_data.get("latitude", 0))
                latitude_dms = ExifUtil.deg_to_dms(latitude,["S", "N"])
                image_metadata['Exif.GPSInfo.GPSLatitudeRef'] = [latitude_dms[3]]
                image_metadata['Exif.GPSInfo.GPSLatitude'] = [latitude_dms[0],latitude_dms[1],latitude_dms[2]]
            if gps_data.longitude:
                longitude = float(gps_data.get("longitude", 0))
                longitude_dms = ExifUtil.deg_to_dms(longitude, ["W", "E"])
                image_metadata['Exif.GPSInfo.GPSLongitudeRef'] = [longitude_dms[3]]
                image_metadata['Exif.GPSInfo.GPSLongitude'] = [longitude_dms[0],longitude_dms[1],longitude_dms[2]]
            if gps_data.altitude:
                image_metadata['Exif.GPSInfo.GPSAltitudeRef'] = self.takeout_metadata.geoDataExif.altitudeRef
