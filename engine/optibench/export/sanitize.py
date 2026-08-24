"""Shared spreadsheet formula-injection sanitizer."""

from __future__ import annotations

from typing import Any

# Characters that can turn a cell value into a formula in Excel / LibreOffice / CSV.
_FORMULA_TRIGGERS = frozenset("=+-@\t\r\n")


def sanitize_spreadsheet_value(val: Any) -> Any:
    """Return a value safe to write into a spreadsheet cell.

    Strings whose first non-whitespace character is a formula trigger are
    prefixed with a single quote so spreadsheet applications treat them as
    plain text. Newlines and carriage returns are normalized to spaces to
    avoid record-breaking attacks.
    """
    if not isinstance(val, str):
        return val
    if not val:
        return val

    # Normalize line breaks to spaces so multi-line payloads cannot break rows.
    cleaned = val.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    stripped = cleaned.lstrip()
    if stripped and stripped[0] in _FORMULA_TRIGGERS:
        return "'" + cleaned
    return cleaned
