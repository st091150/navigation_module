"""
Симуляция прохода по нескольким точкам: mock-привод и график траектории.

Запуск из корня репозитория::

    python examples/demo_navigation.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import matplotlib.pyplot as plt

from navigation_module.config.settings import NavigationSettings
from navigation_module.control.executor import execute_command
from navigation_module.control.interface import MockController
from navigation_module.core.filters import LowPassFilter
from navigation_module.core.gps_utils import GPSOrigin, latlon_to_local_meters, make_origin
from navigation_module.core.navigation import (
    angle_error,
    bearing_to_target,
    distance_to_target,
    generate_command,
    reached_target,
)
from navigation_module.core.orientation import yaw_to_quaternion_z

_EARTH_RADIUS_M = 6_371_000.0


def local_meters_to_latlon(x_m: float, y_m: float, origin: GPSOrigin) -> tuple[float, float]:
    """Обратное плоское преобразование: локальные восток/север → широта/долгота в градусах."""
    dlat_rad = y_m / _EARTH_RADIUS_M
    dlon_rad = x_m / (_EARTH_RADIUS_M * max(origin.cos_lat0, 1e-6))
    lat_deg = (origin.lat0_rad + dlat_rad) * 180.0 / math.pi
    lon_deg = (origin.lon0_rad + dlon_rad) * 180.0 / math.pi
    return lat_deg, lon_deg


def add_gps_noise(lat_deg: float, lon_deg: float, sigma_m: float) -> tuple[float, float]:
    """Грубое смещение в метрах с учётом широты в окрестности точки."""
    noise_e = random.gauss(0.0, sigma_m)
    noise_n = random.gauss(0.0, sigma_m)
    lat0_rad = lat_deg * math.pi / 180.0
    cos_lat = math.cos(lat0_rad)
    dlat = noise_n / _EARTH_RADIUS_M * 180.0 / math.pi
    dlon = noise_e / (_EARTH_RADIUS_M * max(cos_lat, 1e-6)) * 180.0 / math.pi
    return lat_deg + dlat, lon_deg + dlon


class SimpleSimulator:
    """Плоский робот с малым шагом по командам верхнего уровня."""

    def __init__(
        self,
        origin: GPSOrigin,
        start_lat: float,
        start_lon: float,
        start_yaw: float,
        turn_step_deg: float = 12.0,
        move_step_m: float = 0.35,
    ) -> None:
        self.origin = origin
        self.yaw_rad = start_yaw
        x, y = latlon_to_local_meters(start_lat, start_lon, origin)
        self.x_m = x
        self.y_m = y
        self.turn_step_deg = turn_step_deg
        self.move_step_m = move_step_m

    def true_gps(self) -> tuple[float, float]:
        return local_meters_to_latlon(self.x_m, self.y_m, self.origin)

    def apply_turn(self, angle_deg: float) -> None:
        step = math.copysign(min(abs(angle_deg), self.turn_step_deg), angle_deg)
        self.yaw_rad += math.radians(step)

    def apply_move(self, distance_m: float) -> None:
        step = min(distance_m, self.move_step_m)
        self.x_m += math.cos(self.yaw_rad) * step
        self.y_m += math.sin(self.yaw_rad) * step


def run_demo() -> None:
    random.seed(42)
    settings = NavigationSettings()
    origin_ll = (52.520008, 13.404954)
    origin = make_origin(*origin_ll)

    waypoints_ll = [
        origin_ll,
        (52.520208, 13.404954),
        (52.520408, 13.405254),
        (52.520608, 13.405554),
    ]

    sim = SimpleSimulator(origin, *origin_ll, start_yaw=0.0)
    gps_filter = LowPassFilter(alpha=settings.gps_filter_alpha)
    controller = MockController()

    traj_x: list[float] = []
    traj_y: list[float] = []
    headings: list[tuple[float, float, float]] = []

    wp_index = 1
    max_steps = 2500

    print("=== Demo: waypoint navigation (noisy GPS + low-pass) ===")
    for step in range(max_steps):
        if wp_index >= len(waypoints_ll):
            execute_command(controller, {"type": "stop"})
            print("All waypoints reached.")
            break

        target = waypoints_ll[wp_index]
        true_lat, true_lon = sim.true_gps()
        noisy_lat, noisy_lon = add_gps_noise(true_lat, true_lon, sigma_m=0.8)
        filt_lat, filt_lon = gps_filter.filter_point(noisy_lat, noisy_lon)

        cur_gps = (filt_lat, filt_lon)
        if reached_target(cur_gps, target, radius=settings.reach_radius_m):
            print(f"Reached waypoint {wp_index}")
            wp_index += 1
            continue

        dist = distance_to_target(cur_gps, target)
        bear = bearing_to_target(cur_gps, target)
        ae = angle_error(sim.yaw_rad, bear)

        cmd = generate_command(
            dist,
            ae,
            angle_turn_threshold_rad=settings.angle_turn_threshold_rad,
            distance_move_threshold_m=settings.distance_move_threshold_m,
        )

        if cmd["type"] == "turn":
            controller.turn(cmd["angle_deg"])
            sim.apply_turn(cmd["angle_deg"])
        elif cmd["type"] == "move":
            controller.move(cmd["distance_m"])
            sim.apply_move(cmd["distance_m"])
        else:
            execute_command(controller, cmd)

        fx, fy = latlon_to_local_meters(filt_lat, filt_lon, origin)
        traj_x.append(fx)
        traj_y.append(fy)
        headings.append((fx, fy, sim.yaw_rad))

        q = yaw_to_quaternion_z(sim.yaw_rad)
        _ = q  # Пример ориентации в стиле IMU для планировщиков

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(traj_x, traj_y, "-", label="filtered track", color="tab:blue")
    wx = []
    wy = []
    for lat, lon in waypoints_ll:
        gx, gy = latlon_to_local_meters(lat, lon, origin)
        wx.append(gx)
        wy.append(gy)
    ax.scatter(wx, wy, c="tab:red", label="waypoints", zorder=5)
    ax.scatter([traj_x[0]], [traj_y[0]], c="tab:green", label="start", zorder=6)

    skip = max(1, len(headings) // 40)
    scale = 2.0
    for i in range(0, len(headings), skip):
        fx, fy, yaw = headings[i]
        dx = scale * math.cos(yaw)
        dy = scale * math.sin(yaw)
        ax.arrow(fx, fy, dx, dy, head_width=0.4, length_includes_head=True, color="tab:orange")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("East (m)")
    ax.set_ylabel("North (m)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    ax.set_title("Simulated GPS waypoint navigation")

    out_dir = Path(__file__).resolve().parent
    out_png = out_dir / "demo_navigation.png"
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"Saved figure to {out_png}")
    if plt.get_backend().lower() != "agg":
        plt.show()


if __name__ == "__main__":
    run_demo()
