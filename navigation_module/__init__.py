"""Переиспользуемые средства 2D-навигации GPS + IMU и генерация команд."""

from navigation_module.config.settings import NavigationSettings
from navigation_module.control.executor import execute_command
from navigation_module.control.interface import MockController, RobotController
from navigation_module.core.filters import LowPassFilter
from navigation_module.core.geometry import clamp, normalize_angle, normalize_vector
from navigation_module.core.gps_utils import (
    GPSOrigin,
    bearing_between_points,
    gps_distance_meters,
    latlon_to_local_meters,
)
from navigation_module.core.navigation import (
    angle_error,
    bearing_to_target,
    compute_differential_thrust,
    compute_navigation_control,
    distance_to_target,
    generate_command,
    reached_target,
)
from navigation_module.core.orientation import quaternion_to_yaw
from navigation_module.io.output import write_navigation_output
from navigation_module.io.template import format_command

__all__ = [
    "NavigationSettings",
    "RobotController",
    "MockController",
    "execute_command",
    "LowPassFilter",
    "clamp",
    "normalize_angle",
    "normalize_vector",
    "GPSOrigin",
    "bearing_between_points",
    "gps_distance_meters",
    "latlon_to_local_meters",
    "distance_to_target",
    "bearing_to_target",
    "angle_error",
    "reached_target",
    "compute_navigation_control",
    "compute_differential_thrust",
    "generate_command",
    "quaternion_to_yaw",
    "write_navigation_output",
    "format_command",
]
