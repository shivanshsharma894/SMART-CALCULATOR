"""Unit converter: length, mass, time, data, volume, speed, area and temperature."""
import math
from typing import Dict

from .exceptions import UnitError

UNITS: Dict[str, Dict[str, float]] = {
    "length": {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344,
               "yd": 0.9144, "ft": 0.3048, "in": 0.0254},
    "mass": {"kg": 1, "g": 0.001, "mg": 1e-6, "t": 1000, "lb": 0.45359237, "oz": 0.028349523125},
    "time": {"s": 1, "ms": 0.001, "min": 60, "h": 3600, "day": 86400, "week": 604800},
    "data": {"byte": 1, "kb": 1024, "mb": 1024 ** 2, "gb": 1024 ** 3, "tb": 1024 ** 4},
    "volume": {"l": 1, "ml": 0.001, "gal": 3.785411784, "cup": 0.2365882365},
    "speed": {"m/s": 1, "km/h": 1 / 3.6, "mph": 0.44704, "knot": 1852 / 3600},
    "area": {"m2": 1, "km2": 1e6, "ha": 1e4, "acre": 4046.8564224, "ft2": 0.09290304},
}
TEMPERATURE = {"c", "f", "k"}


def find_category(unit: str) -> str:
    unit = unit.strip().lower()
    if unit in TEMPERATURE:
        return "temperature"
    for category, table in UNITS.items():
        if unit in table:
            return category
    raise UnitError(f"Unknown unit '{unit}'. Type :units to list supported units")


def list_units() -> Dict[str, list]:
    out = {cat: sorted(table) for cat, table in UNITS.items()}
    out["temperature"] = sorted(TEMPERATURE)
    return out


def _to_celsius(v, unit):
    return {"c": v, "f": (v - 32) * 5 / 9, "k": v - 273.15}[unit]


def _from_celsius(c, unit):
    return {"c": c, "f": c * 9 / 5 + 32, "k": c + 273.15}[unit]


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert ``value`` between two units of the same category."""
    if not isinstance(value, (int, float)) or math.isnan(value) or math.isinf(value):
        raise UnitError("Value must be a finite number")
    f, t = from_unit.strip().lower(), to_unit.strip().lower()
    cat_f, cat_t = find_category(f), find_category(t)
    if cat_f != cat_t:
        raise UnitError(f"Cannot convert {cat_f} ({f}) to {cat_t} ({t})")
    if cat_f == "temperature":
        celsius = _to_celsius(value, f)
        if celsius < -273.15 - 1e-9:
            raise UnitError("Temperature is below absolute zero")
        return _from_celsius(celsius, t)
    table = UNITS[cat_f]
    return value * table[f] / table[t]
