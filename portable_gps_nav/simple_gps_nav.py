"""
Автономный минимум: расстояние между точками WGS84 (градусы) и углы для робота.

Не зависит от пакета navigation_module — можно скопировать только эту папку.

Используется та же математика, что в navigation_module.core.gps_utils / geometry / navigation:
гаверсинус для расстояния, пеленг в радианах с конвенцией atan2 (ось x на восток).
"""

from __future__ import annotations

import math
from typing import Tuple

_EARTH_RADIUS_M = 6_371_000.0


def _deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180.0


def normalize_angle(angle_rad: float) -> float:
    """Свернуть угол в интервал (-π, π]."""
    return math.atan2(math.sin(angle_rad), math.cos(angle_rad))


def gps_distance_meters(
    lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float
) -> float:
    """Расстояние по дуге большого круга (метры), формула гаверсинуса."""
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
    Начальный пеленг из точки 1 в точку 2 (радианы).
    Матем. угол: 0 радиан — направление оси +x (восток), как для atan2(dy, dx) на локальной плоскости.
    """
    phi1 = _deg_to_rad(lat1_deg)
    phi2 = _deg_to_rad(lat2_deg)
    dlamb = _deg_to_rad(lon2_deg - lon1_deg)
    y = math.sin(dlamb) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(
        dlamb
    )
    bearing_geo = math.atan2(y, x)
    return math.pi / 2.0 - bearing_geo


def distance_to_target(
    current_gps: Tuple[float, float], target_gps: Tuple[float, float]
) -> float:
    """Расстояние от текущей точки (широта, долгота) в градусах до цели — метры."""
    lat_c, lon_c = current_gps
    lat_t, lon_t = target_gps
    return gps_distance_meters(lat_c, lon_c, lat_t, lon_t)


def bearing_to_target(
    current_gps: Tuple[float, float], target_gps: Tuple[float, float]
) -> float:
    """Пеленг «куда смотреть» на цель от текущей позиции, радианы, интервал (-π, π]."""
    lat_c, lon_c = current_gps
    lat_t, lon_t = target_gps
    return normalize_angle(bearing_between_points(lat_c, lon_c, lat_t, lon_t))


def angle_error(current_yaw_rad: float, target_bearing_rad: float) -> float:
    """
    На сколько нужно повернуться (радианы, (-π, π]), чтобы смотреть на цель.
    current_yaw_rad и target_bearing_rad должны быть в одной и той же системе (как у вашего робота).
    """
    return normalize_angle(target_bearing_rad - current_yaw_rad)


def turn_angle_to_goal_rad(
    current_yaw_rad: float,
    robot_lat_deg: float,
    robot_lon_deg: float,
    goal_lat_deg: float,
    goal_lon_deg: float,
) -> float:
    """Один вызов: угол поворота к цели при известном yaw робота и GPS точках."""
    bearing = bearing_to_target(
        (robot_lat_deg, robot_lon_deg), (goal_lat_deg, goal_lon_deg)
    )
    return angle_error(current_yaw_rad, bearing)
