"""Абстракция контроллера и заглушка «железа»."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RobotController(ABC):
    """Аппаратная абстракция: подключайте робота через наследование."""

    @abstractmethod
    def turn(self, angle_deg: float) -> None:
        """Разворот на месте на угол (градусы; знак — по вашей конвенции направления)."""

    @abstractmethod
    def move(self, distance_m: float) -> None:
        """Проехать вперёд примерно distance_m метров."""

    @abstractmethod
    def stop(self) -> None:
        """Остановка."""


class MockController(RobotController):
    """Контроллер только с печатью в консоль — для симуляции или отладки."""

    def turn(self, angle_deg: float) -> None:
        print(f"[MOCK] TURN {angle_deg:.4g} deg")

    def move(self, distance_m: float) -> None:
        print(f"[MOCK] MOVE {distance_m:.4g} m")

    def stop(self) -> None:
        print("[MOCK] STOP")
