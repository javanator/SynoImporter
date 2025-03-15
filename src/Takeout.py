"""
This file is also AI garbage. Clean it up later
TODO: Add typing for awesomeness

"""

import json
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import piexif
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

class PhotoMetadata(BaseModel):
    title: str
    description: str
    imageViews: str
    creationTime: TimeInfo
    photoTakenTime: TimeInfo
    geoData: GeoData
    geoDataExif: GeoData
    url: str
    googlePhotosOrigin: GooglePhotosOrigin

class Takeout:
    def read_google_takeout_json(photo_metadata: PhotoMetadata) -> Dict[str, dict]:
        # Create EXIF-style dictionary
        exif_data = {
            "0th": {},  # Basic metadata (Model, Make, etc.)
            "Exif": {},  # Timestamps and other detailed metadata
            "GPS": {},  # GPS coordinates
            "1st": {},  # Thumbnails and unused data
        }

        # Map "title", "description", "cameraMake", and "cameraModel" to "0th" tags
        if photo_metadata.title:
            exif_data["0th"][piexif.ImageIFD.ImageDescription] = photo_metadata.title.encode("utf-8")  # Image title
        if "description" in photo_metadata.description:
            exif_data["0th"][piexif.ImageIFD.XPComment] = photo_metadata.description.encode("utf-16")  # Optional description

        # Map creation time (timestamps) to "Exif" tags
        if photo_metadata.photoTakenTime and photo_metadata.photoTakenTime.timestamp:
            timestamp = photo_metadata.photoTakenTime.timestamp
            human_readable_time = photo_metadata.photoTakenTime.formatted
            if timestamp:
                # Convert timestamp to a formatted date (if not provided as "formatted")
                dt = datetime.fromtimestamp(int(timestamp))
                formatted_time = human_readable_time or dt.strftime("%Y:%m:%d %H:%M:%S")
                exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal] = formatted_time.encode("utf-8")

        # Map GPS data to "GPS" tags
        if photo_metadata.geoDataExif:
            gps_data = photo_metadata.geoDataExif
            exif_data["GPS"][piexif.GPSIFD.GPSVersionID] = (2,0,0,0)

            if gps_data.latitude:
                latitude = float(gps_data.get("latitude", 0))
                dms = ExifUtil.deg_to_dms(latitude,["S", "N"])
                exif_latitude = ExifUtil.dms_to_exif_format(dms[0], dms[1], dms[2])
                exif_data["GPS"][piexif.GPSIFD.GPSLatitude] = exif_latitude
                exif_data["GPS"][piexif.GPSIFD.GPSLatitudeRef] = dms[3]
            if gps_data.longitude:
                longitude = float(gps_data.get("longitude", 0))
                dms = ExifUtil.deg_to_dms(longitude, ["W", "E"])
                exif_data["GPS"][piexif.GPSIFD.GPSLongitude] = ExifUtil.dms_to_exif_format(dms[0], dms[1], dms[2])
                exif_data["GPS"][piexif.GPSIFD.GPSLongitudeRef] = dms[3]
            if gps_data.altitude:
                exif_data["GPS"][piexif.GPSIFD.GPSAltitude] = (int(gps_data["altitude"]), 1)

        # Return formatted EXIF data dictionary
        return exif_data