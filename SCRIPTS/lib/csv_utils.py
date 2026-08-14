"""Ported 1:1 from scripts/lib/csv.js. Hand-rolled (not Python's csv module)
to preserve identical escaping/line-ending behavior to the original."""
import json
import re

_NEEDS_QUOTING = re.compile(r'[",\n\r]')


def _escape_cell(value):
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    if _NEEDS_QUOTING.search(text):
        return '"' + text.replace('"', '""') + '"'
    return text


def to_csv(rows, columns):
    header = ",".join(columns)
    lines = [",".join(_escape_cell(row.get(col)) for col in columns) for row in rows]
    return "\r\n".join([header, *lines]) + "\r\n"
