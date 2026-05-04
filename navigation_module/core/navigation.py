"""Navigation primitives: distance, bearing, errors, control, commands."""

from __future__ import annotations

import math
from typing import Any, Dict

from navigation_module.core.geometry import clamp, normalize_angle
from navigation_module.core.gps_utils import bearing_between_points, gps_distance_meters


def distance_to_target(
    current_gps: tuple[float, float], target_gps: tuple[float, float]
) -> float:
    """Haversine distance from current (lat, lon) deg to target (lat, lon) deg."""
    lat_c, lon_c = current_gps
    lat_t, lon_t = target_gps
    return gps_distance_meters(lat_c, lon_c, lat_t, lon_t)


def bearing_to_target(
    current_gps: tuple[float, float], target_gps: tuple[float, float]
) -> float:
    """Bearing from current to target (radians, consistent with local atan2 frame)."""
    lat_c, lon_c = current_gps
    lat_t, lon_t = target_gps
    return normalize_angle(bearing_between_points(lat_c, lon_c, lat_t, lon_t))


def angle_error(current_yaw_rad: float, target_bearing_rad: float) -> float:
    """Normalized steering error using atan2(sin, cos)."""
    return normalize_angle(target_bearing_rad - current_yaw_rad)


def reached_target(
    current_gps: tuple[float, float],
    target_gps: tuple[float, float],
    radius: float = 1.0,
) -> bool:
    """True if within tolerance radius (meters)."""
    return distance_to_target(current_gps, target_gps) <= radius


def compute_navigation_control(
    distance_m: float,
    angle_error_rad: float,
    k1: float,
    k2: float,
) -> tuple[float, float]:
    """
    Simple posture-based drive commands.

    F = k1 * distance * cos(angle_error)
    T = k2 * angle_error
    """
    f_linear = k1 * distance_m * math.cos(angle_error_rad)
    t_angular = k2 * angle_error_rad
    return f_linear, t_angular


def compute_differential_thrust(
    f_linear: float,
    t_angular: float,
    thrust_limit: float | None = None,
) -> tuple[float, float]:
    """
    Map (F, T) to left/right differential thrust channels.

    left = F - T, right = F + T (sign convention can be swapped per robot).
    Optional symmetric clamp on magnitude.
    """
    left = f_linear - t_angular
    right = f_linear + t_angular
    if thrust_limit is not None and thrust_limit > 0:
        left = clamp(left, -thrust_limit, thrust_limit)
        right = clamp(right, -thrust_limit, thrust_limit)
    return left, right


def generate_command(
    distance_m: float,
    angle_error_rad: float,
    angle_turn_threshold_rad: float,
    distance_move_threshold_m: float,
) -> Dict[str, Any]:
    """
    Discrete high-level motion primitives.

    Priority: large heading error → turn; else need to translate → move; else stop.
    Angles in returned dict are degrees.
    """
    ae = abs(normalize_angle(angle_error_rad))
    if ae > angle_turn_threshold_rad:
        deg = math.degrees(normalize_angle(angle_error_rad))
        return {"type": "turn", "angle_deg": deg}
    if distance_m > distance_move_threshold_m:
        return {"type": "move", "distance_m": float(distance_m)}
    return {"type": "stop"}
