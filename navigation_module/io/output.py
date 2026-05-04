"""Configurable serialization of navigation artifacts."""

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
    Return or persist navigation output.

    - dict: returns Python dict unchanged (caller convenience).
    - json: JSON string.
    - file: writes JSON to ``file_path`` (required); returns path string.
    """
    if output_mode == "dict":
        return data
    if output_mode == "json":
        return json.dumps(data, indent=2)
    if output_mode == "file":
        if file_path is None:
            raise ValueError("file_path is required when output_mode='file'")
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(path.resolve())
    raise ValueError(f"Unknown output_mode: {output_mode!r}")
