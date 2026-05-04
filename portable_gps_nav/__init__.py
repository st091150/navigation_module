"""
Портативная копия формул GPS-навигации без установки основного проекта.

См. также модуль simple_gps_nav и README.md в этой папке.
"""

from .simple_gps_nav import (
    angle_error,
    bearing_between_points,
    bearing_to_target,
    distance_to_target,
    gps_distance_meters,
    normalize_angle,
    turn_angle_to_goal_rad,
)

__all__ = [
    "angle_error",
    "bearing_between_points",
    "bearing_to_target",
    "distance_to_target",
    "gps_distance_meters",
    "normalize_angle",
    "turn_angle_to_goal_rad",
]
