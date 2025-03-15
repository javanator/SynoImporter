'''
This file is AI garbage. Clean it up later.
TODO: Add types
'''

from fractions import Fraction
from typing import Any, Dict

import piexif
from PIL import Image


def deg_to_dms(decimal_coordinate, cardinal_directions):
    """
    This function converts decimal coordinates into the DMS (degrees, minutes and seconds) format.
    It also determines the cardinal direction of the coordinates.

    :param decimal_coordinate: the decimal coordinates, such as 34.0522
    :param cardinal_directions: the locations of the decimal coordinate, such as ["S", "N"] or ["W", "E"]
    :return: degrees, minutes, seconds and compass_direction
    :rtype: int, int, float, string
    """
    if decimal_coordinate < 0:
        compass_direction = cardinal_directions[0]
    elif decimal_coordinate > 0:
        compass_direction = cardinal_directions[1]
    else:
        compass_direction = ""
    degrees = int(abs(decimal_coordinate))
    decimal_minutes = (abs(decimal_coordinate) - degrees) * 60
    minutes = int(decimal_minutes)
    seconds = Fraction((decimal_minutes - minutes) * 60).limit_denominator(100)
    return degrees, minutes, seconds, compass_direction

def dms_to_exif_format(dms_degrees, dms_minutes, dms_seconds):
    """
    This function converts DMS (degrees, minutes and seconds) to values that can
    be used with the EXIF (Exchangeable Image File Format).

    :param dms_degrees: int value for degrees
    :param dms_minutes: int value for minutes
    :param dms_seconds: fractions.Fraction value for seconds
    :return: EXIF values for the provided DMS values
    :rtype: nested tuple
    """
    exif_format = (
        (dms_degrees, 1),
        (dms_minutes, 1),
        (int(dms_seconds.limit_denominator(100).numerator), int(dms_seconds.limit_denominator(100).denominator))
    )
    return exif_format

def merge_exif_data(existing_exif_dict: Dict[str,Any], new_exif_dict: Dict[str,Any])-> Dict[str,Any]:
    if existing_exif_dict is not None:
        modified_exif_dict = existing_exif_dict
    else:
        modified_exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    for ifd_type, exif_tags in new_exif_dict.items():
        existing_ifd_data = modified_exif_dict.get(ifd_type, {})
        for tag_key, tag_value in exif_tags.items():
            if tag_key not in existing_ifd_data:  # Add custom data if it doesn't exist
                existing_ifd_data[tag_key] = tag_value
        modified_exif_dict[ifd_type] = existing_ifd_data

    # Validate EXIF data before returning
    return modified_exif_dict

def load_exif_data(image :Image):
    # Read the EXIF data
    raw_exif_data = image.info.get("exif", None)

    if raw_exif_data is None:
        print("No EXIF data found in the image.")
        return {}

    # Convert the raw EXIF data into a structured dictionary
    exif_data = piexif.load(raw_exif_data)
    return exif_data