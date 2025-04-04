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
