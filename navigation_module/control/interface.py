"""Controller abstraction and mock hardware."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RobotController(ABC):
    """Hardware abstraction: integrate your robot by subclassing."""

    @abstractmethod
    def turn(self, angle_deg: float) -> None:
        """Rotate in place by angle (degrees, sign = direction convention)."""

    @abstractmethod
    def move(self, distance_m: float) -> None:
        """Drive forward approximately distance_m meters."""

    @abstractmethod
    def stop(self) -> None:
        """Halt motion."""


class MockController(RobotController):
    """Print-only controller for simulation or debugging."""

    def turn(self, angle_deg: float) -> None:
        print(f"[MOCK] TURN {angle_deg:.4g} deg")

    def move(self, distance_m: float) -> None:
        print(f"[MOCK] MOVE {distance_m:.4g} m")

    def stop(self) -> None:
        print("[MOCK] STOP")
