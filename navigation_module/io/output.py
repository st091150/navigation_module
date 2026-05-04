"""Настраиваемая сериализация результатов навигации."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

OutputMode = Literal["dict", "json", "file"]


def write_navigation_output(
    data: dict[str, Any],
    output_mode: OutputMode,
    *,
    file_path: str | Path | None = None,
) -> str | dict[str, Any] | None:
    """
    Вернуть или сохранить вывод навигации.

    - dict: вернуть словарь Python без изменений (удобство для вызывающего кода).
    - json: строка JSON.
    - file: записать JSON в ``file_path`` (обязателен); вернуть путь строкой.
    """
    if output_mode == "dict":
        return data
    if output_mode == "json":
        return json.dumps(data, indent=2)
    if output_mode == "file":
        if file_path is None:
            raise ValueError("При output_mode='file' нужно указать file_path")
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(path.resolve())
    raise ValueError(f"Неизвестный output_mode: {output_mode!r}")
