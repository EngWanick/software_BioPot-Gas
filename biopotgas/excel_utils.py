from __future__ import annotations

from typing import Any, Dict


def to_bool(value: Any, default: bool = True) -> bool:
    if value is None or value == "":
        return default

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "sim", "s"}:
        return True

    if text in {"false", "0", "no", "não", "nao", "n"}:
        return False

    return default

def to_float(value: Any, field_name: str, row_number: int | None = None) -> float:
    if value is None or value == "":
        return 0.0
    
    try:
        return float(value)    
    except Exception as exc:
        location = f" at row {row_number}" if row_number else ""
        raise ValueError(
            f"Invalid numeric value for {field_name}{location}: {value!r}"
        ) from exc


def get_header_map(ws, header_row: int) -> Dict[str, int]:
    values = [
        ws.cell(row=header_row, column=col).value
        for col in range(1, ws.max_column + 1)
    ]

    return {
        str(value).strip(): index + 1
        for index, value in enumerate(values)
        if value is not None and str(value).strip()
    }