"""Map structured navigation commands to controller calls."""

from __future__ import annotations

from typing import Any, Mapping

from navigation_module.control.interface import RobotController


def execute_command(controller: RobotController, command: Mapping[str, Any]) -> None:
    """Dispatch dict commands from generate_command."""
    cmd_type = command.get("type")
    if cmd_type == "turn":
        controller.turn(float(command["angle_deg"]))
    elif cmd_type == "move":
        controller.move(float(command["distance_m"]))
    elif cmd_type == "stop":
        controller.stop()
    else:
        raise ValueError(f"Unknown command type: {cmd_type!r}")
