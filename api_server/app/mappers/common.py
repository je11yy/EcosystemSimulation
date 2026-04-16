from datetime import datetime


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def position(x: float, y: float) -> dict[str, float]:
    return {"x": x, "y": y}
