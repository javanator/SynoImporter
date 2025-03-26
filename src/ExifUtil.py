from fractions import Fraction
from typing import Any, Dict
import math as math


def deg_to_dms(decimal_coordinate: float, cardinal_directions: list[str])-> tuple[Fraction, Fraction, Fraction, str]:
    """
    This function converts decimal coordinates into the DMS (degrees, minutes and seconds) format.
    It also determines the cardinal direction of the coordinates.

    :param decimal_coordinate: the decimal coordinates, such as 34.0522
    :param cardinal_directions: the locations of the decimal coordinate, such as ["S", "N"] or ["W", "E"]
    :return: degrees, minutes, seconds and compass_direction
    :rtype: Fraction, Fraction, Fraction, int
    """
    compass_direction: str = ""
    if decimal_coordinate < 0:
        compass_direction = cardinal_directions[0]
    elif decimal_coordinate > 0:
        compass_direction = cardinal_directions[1]

    absolute = abs(decimal_coordinate)
    degrees = float(math.floor(absolute))
    minutes_not_truncated = (absolute - degrees) * 60
    minutes = float(math.floor(minutes_not_truncated))
    seconds = float(math.floor((minutes_not_truncated - minutes) * 60))

    return Fraction(degrees).limit_denominator(1), Fraction(minutes).limit_denominator(1), Fraction(seconds).limit_denominator(100000), compass_direction

# def load_exif_data(image :Image):
#     # Read the EXIF data
#     raw_exif_data = image.info.get("exif", None)
#
#     if raw_exif_data is None:
#         print("No EXIF data found in the image.")
#         return {}
#
#     # Convert the raw EXIF data into a structured dictionary
#     exif_data = piexif.load(raw_exif_data)
#     return exif_data
#
# def scanexif(image :Image):
#     img_exif = image.getexif()
#
#     IFD_CODE_LOOKUP = {i.value: i.name for i in ExifTags.IFD}
#     for tag_code, value in img_exif.items():
#         # if the tag is an IFD block, nest into it
#         if tag_code in IFD_CODE_LOOKUP:
#             ifd_tag_name = IFD_CODE_LOOKUP[tag_code]
#             print(f"IFD '{ifd_tag_name}' (code {tag_code}):")
#             ifd_data = img_exif.get_ifd(tag_code).items()
#             for nested_key, nested_value in ifd_data:
#                 nested_tag_name = ExifTags.GPSTAGS.get(nested_key, None) or ExifTags.TAGS.get(nested_key, None) or nested_key
#                 print(f"  {nested_tag_name}: {nested_value}")
#         else:
#             # root-level tag
#             print(f"{ExifTags.TAGS.get(tag_code)}: {value}")
