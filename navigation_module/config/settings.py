"""Параметры настройки навигации."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NavigationSettings:
    """Пороги и коэффициенты для генерации команд и низкоуровневого управления."""

    k_distance: float = 0.5
    k_heading: float = 1.2
    angle_turn_threshold_rad: float = 0.15
    distance_move_threshold_m: float = 0.5
    reach_radius_m: float = 1.0
    gps_filter_alpha: float = 0.35
    thrust_limit: float | None = 1.0
