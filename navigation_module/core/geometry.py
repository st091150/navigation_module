"""Basic geometric helpers: angles, vectors, clamping."""

from __future__ import annotations

import math
from typing import Tuple


def normalize_angle(angle_rad: float) -> float:
    """Wrap angle to (-π, π]."""
    return math.atan2(math.sin(angle_rad), math.cos(angle_rad))


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to [low, high]."""
    return max(low, min(high, value))


def normalize_vector(vx: float, vy: float) -> Tuple[float, float]:
    """Return unit vector or (0, 0) if length is ~0."""
    length = math.hypot(vx, vy)
    if length < 1e-12:
        return 0.0, 0.0
    return vx / length, vy / length
