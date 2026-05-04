"""Интеграционные проверки выходов управления и диспетчеризации команд."""

import math

import pytest

from navigation_module.config.settings import NavigationSettings
from navigation_module.control.executor import execute_command
from navigation_module.control.interface import MockController
from navigation_module.core.filters import LowPassFilter
from navigation_module.core.navigation import (
    compute_differential_thrust,
    compute_navigation_control,
    generate_command,
)
from navigation_module.io.output import write_navigation_output
from navigation_module.io.template import format_command


def test_generate_command_turn_priority():
    cmd = generate_command(
        distance_m=10.0,
        angle_error_rad=math.radians(40),
        angle_turn_threshold_rad=math.radians(10),
        distance_move_threshold_m=0.5,
    )
    assert cmd["type"] == "turn"
    assert "angle_deg" in cmd


def test_generate_command_move():
    cmd = generate_command(
        distance_m=5.0,
        angle_error_rad=0.01,
        angle_turn_threshold_rad=0.2,
        distance_move_threshold_m=0.5,
    )
    assert cmd["type"] == "move"
    assert cmd["distance_m"] == 5.0


def test_generate_command_stop():
    cmd = generate_command(
        distance_m=0.2,
        angle_error_rad=0.01,
        angle_turn_threshold_rad=0.2,
        distance_move_threshold_m=0.5,
    )
    assert cmd == {"type": "stop"}


def test_control_law_shapes():
    F, T = compute_navigation_control(5.0, 0.0, k1=1.0, k2=2.0)
    assert math.isclose(F, 5.0)
    assert math.isclose(T, 0.0)
    F2, T2 = compute_navigation_control(5.0, math.pi / 2, k1=1.0, k2=2.0)
    assert math.isclose(F2, 0.0, abs_tol=1e-15)
    left, right = compute_differential_thrust(F2, T2, thrust_limit=None)
    assert math.isclose(left, -T2) and math.isclose(right, T2)


def test_execute_command_mock(capsys):
    ctrl = MockController()
    execute_command(ctrl, {"type": "turn", "angle_deg": 15.0})
    execute_command(ctrl, {"type": "move", "distance_m": 2.0})
    execute_command(ctrl, {"type": "stop"})
    out = capsys.readouterr().out
    assert "[MOCK] TURN" in out and "[MOCK] MOVE" in out and "[MOCK] STOP" in out


def test_execute_unknown_raises():
    with pytest.raises(ValueError):
        execute_command(MockController(), {"type": "spin"})


def test_output_modes(tmp_path):
    data = {"cmd": "stop"}
    assert write_navigation_output(data, "dict") == data
    js = write_navigation_output(data, "json")
    assert '"stop"' in js
    p = tmp_path / "out.json"
    path = write_navigation_output(data, "file", file_path=p)
    assert path == str(p.resolve())
    assert p.read_text(encoding="utf-8").strip()


def test_template_safe_missing():
    s = format_command("MOVE {distance_m:.2f} x={extra}", {"distance_m": 1.234}, safe=True)
    assert "1.23" in s
    assert "x=" in s


def test_low_pass_smoothing():
    f = LowPassFilter(alpha=0.5, initial_lat=0.0, initial_lon=0.0)
    la, lo = f.filter_point(1.0, 1.0)
    assert la == 0.5 and lo == 0.5


def test_settings_defaults():
    s = NavigationSettings()
    assert s.reach_radius_m > 0
