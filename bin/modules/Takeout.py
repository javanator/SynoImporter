"""
This file is also AI garbage. Clean it up later
TODO: Add typing for awesomeness

"""

import json

import piexif

from bin.modules import ExifUtil


def read_google_takeout_json(data :json):
    # Create EXIF-style dictionary
    exif_data = {
        "0th": {},  # Basic metadata (Model, Make, etc.)
        "Exif": {},  # Timestamps and other detailed metadata
        "GPS": {},  # GPS coordinates
        "1st": {},  # Thumbnails and unused data
    }

    # Map "title", "description", "cameraMake", and "cameraModel" to "0th" tags
    if "title" in data:
        exif_data["0th"][piexif.ImageIFD.ImageDescription] = data["title"].encode("utf-8")  # Image title
    if "description" in data:
        exif_data["0th"][piexif.ImageIFD.XPComment] = data["description"].encode("utf-16")  # Optional description
    if "cameraMake" in data:
        exif_data["0th"][piexif.ImageIFD.Make] = data["cameraMake"].encode("utf-8")  # Camera make
    if "cameraModel" in data:
        exif_data["0th"][piexif.ImageIFD.Model] = data["cameraModel"].encode("utf-8")  # Camera model

    # Map creation time (timestamps) to "Exif" tags
    if "photoTakenTime" in data and "timestamp" in data["photoTakenTime"]:
        timestamp = data["photoTakenTime"]["timestamp"]
        human_readable_time = data["photoTakenTime"].get("formatted", None)
        if timestamp:
            # Convert timestamp to a formatted date (if not provided as "formatted")
            import datetime
            dt = datetime.datetime.fromtimestamp(int(timestamp))
            formatted_time = human_readable_time or dt.strftime("%Y:%m:%d %H:%M:%S")
            exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal] = formatted_time.encode("utf-8")

    # Map GPS data to "GPS" tags
    if "geoDataExif" in data:
        gps_data = data["geoDataExif"]
        exif_data["GPS"][piexif.GPSIFD.GPSVersionID] = (2,0,0,0)
        if "latitude" in gps_data:
            latitude = float(gps_data.get("latitude", 0))
            dms = ExifUtil.deg_to_dms(latitude,["S", "N"])
            exif_latitude = ExifUtil.dms_to_exif_format(dms[0], dms[1], dms[2])
            exif_data["GPS"][piexif.GPSIFD.GPSLatitude] = exif_latitude
            exif_data["GPS"][piexif.GPSIFD.GPSLatitudeRef] = dms[3]
        if "longitude" in gps_data:
            longitude = float(gps_data.get("longitude", 0))
            dms = ExifUtil.deg_to_dms(longitude, ["W", "E"])
            exif_data["GPS"][piexif.GPSIFD.GPSLongitude] = ExifUtil.dms_to_exif_format(dms[0], dms[1], dms[2])
            exif_data["GPS"][piexif.GPSIFD.GPSLongitudeRef] = dms[3]
        if "altitude" in gps_data:
            exif_data["GPS"][piexif.GPSIFD.GPSAltitude] = (int(gps_data["altitude"]), 1)

    # Return formatted EXIF data dictionary
    return exif_data