"""GPS helpers: local tangent plane meters from first fix, distance, bearing."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

# Mean Earth radius (meters)
_EARTH_RADIUS_M = 6_371_000.0


@dataclass
class GPSOrigin:
    """Origin for local ENU-style XY (x=east, y=north) in meters."""

    lat0_rad: float
    lon0_rad: float
    cos_lat0: float


def _deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180.0


def make_origin(lat_deg: float, lon_deg: float) -> GPSOrigin:
    """Build origin from the first GPS reading."""
    lat0 = _deg_to_rad(lat_deg)
    lon0 = _deg_to_rad(lon_deg)
    return GPSOrigin(lat0_rad=lat0, lon0_rad=lon0, cos_lat0=math.cos(lat0))


def latlon_to_local_meters(
    lat_deg: float, lon_deg: float, origin: GPSOrigin
) -> Tuple[float, float]:
    """
    Flat-earth approximation: x east (m), y north (m) relative to origin.
    Adequate for typical outdoor robot neighborhoods (km scale).
    """
    lat = _deg_to_rad(lat_deg)
    lon = _deg_to_rad(lon_deg)
    dlat = lat - origin.lat0_rad
    dlon = lon - origin.lon0_rad
    x = dlon * origin.cos_lat0 * _EARTH_RADIUS_M
    y = dlat * _EARTH_RADIUS_M
    return x, y


def gps_distance_meters(
    lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float
) -> float:
    """Great-circle distance via haversine formula (meters)."""
    phi1 = _deg_to_rad(lat1_deg)
    phi2 = _deg_to_rad(lat2_deg)
    dphi = _deg_to_rad(lat2_deg - lat1_deg)
    dlamb = _deg_to_rad(lon2_deg - lon1_deg)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlamb / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return _EARTH_RADIUS_M * c


def bearing_between_points(
    lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float
) -> float:
    """
    Initial bearing from point 1 to point 2 (radians, math angle: 0 = +x east).
    Converts from navigational bearing (clockwise from north) for flat mapping.
    """
    phi1 = _deg_to_rad(lat1_deg)
    phi2 = _deg_to_rad(lat2_deg)
    dlamb = _deg_to_rad(lon2_deg - lon1_deg)
    y = math.sin(dlamb) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(
        dlamb
    )
    bearing_geo = math.atan2(y, x)
    # math convention: x=east, y=north → yaw from +x is (π/2 - geo_bearing_from_north)
    return math.pi / 2.0 - bearing_geo
