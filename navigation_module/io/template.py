"""Пользовательские строковые шаблоны с опционально «мягким» форматированием."""

from __future__ import annotations

import string
from typing import Any, Mapping


class _SoftFormatter(string.Formatter):
    """При отсутствии ключа подставлять пустую строку вместо исключения."""

    def get_value(self, key: Any, args: Any, kwds: Mapping[str, Any]) -> Any:  # type: ignore[override]
        try:
            return super().get_value(key, args, kwds)
        except KeyError:
            return ""

    def format_field(self, value: Any, format_spec: str) -> str:  # type: ignore[override]
        if value == "":
            return ""
        return super().format_field(value, format_spec)


def format_command(template: str, data: Mapping[str, Any], safe: bool = True) -> str:
    """
    Подставить в *template* значения из *data*.

    Если ``safe`` истина, отсутствующие плейсхолдеры дают пустые строки.
    """
    if safe:
        return _SoftFormatter().format(template, **dict(data))
    return template.format(**dict(data))
