import re
from datetime import date, datetime


def parse_int_id(value: str | int, campo: str = "paciente_id") -> int | None:
    if isinstance(value, int):
        return value
    text = str(value).strip().strip('"').strip("'")
    if text.isdigit():
        return int(text)
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return None


def parse_limite(value: str | int | None, default: int = 5) -> int:
    if value is None or value == "":
        return default
    parsed = parse_int_id(value, "limite")
    return parsed if parsed is not None else default


def parse_data(value: str | date | None) -> date | None:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, date):
        return value
    texto = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None
