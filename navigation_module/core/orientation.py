"""Orientation conversions (quaternion ↔ yaw)."""

from __future__ import annotations

import math
from typing import Tuple

from navigation_module.core.geometry import normalize_angle


def quaternion_to_yaw(x: float, y: float, z: float, w: float) -> float:
    """
    Extract yaw (rotation about Z) in radians.

    Uses XYZW quaternion convention common in ROS (geometry_msgs).
    Yaw is in the robot/plane frame consistent with atan2(dy, dx) navigation.
    """
    # yaw from quaternion (ZYX / planar yaw)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return normalize_angle(math.atan2(siny_cosp, cosy_cosp))


def yaw_to_quaternion_z(z_yaw_rad: float) -> Tuple[float, float, float, float]:
    """Minimal helper: pure yaw quaternion (x, y, z, w)."""
    half = z_yaw_rad * 0.5
    return 0.0, 0.0, math.sin(half), math.cos(half)
