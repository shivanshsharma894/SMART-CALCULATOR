"""Basic descriptive statistics implemented from first principles."""
import math
import re
from collections import Counter
from typing import Dict, List

from .exceptions import StatsError


def parse_numbers(text: str) -> List[float]:
    """Parse '1, 2 3.5' into a list of floats."""
    parts = [p for p in re.split(r"[,\s]+", text.strip()) if p]
    if not parts:
        raise StatsError("Provide at least one number")
    try:
        values = [float(p) for p in parts]
    except ValueError as exc:
        raise StatsError(f"Invalid number in list: {exc}")
    if any(math.isnan(v) or math.isinf(v) for v in values):
        raise StatsError("Values must be finite")
    return values


def _require(data):
    if not data:
        raise StatsError("Data set is empty")


def mean(data: List[float]) -> float:
    _require(data)
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    _require(data)
    s, n = sorted(data), len(data)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def mode(data: List[float]) -> List[float]:
    """All most-frequent values (empty list if every value is unique)."""
    _require(data)
    counts = Counter(data)
    top = max(counts.values())
    return [] if top == 1 and len(counts) > 1 else sorted(k for k, v in counts.items() if v == top)


def variance(data: List[float], sample: bool = True) -> float:
    _require(data)
    n = len(data)
    if sample and n < 2:
        raise StatsError("Sample variance needs at least two values")
    m = mean(data)
    return sum((x - m) ** 2 for x in data) / (n - 1 if sample else n)


def std_dev(data: List[float], sample: bool = True) -> float:
    return math.sqrt(variance(data, sample))


def describe(data: List[float]) -> Dict[str, object]:
    """Summary of a data set."""
    _require(data)
    out = {
        "count": len(data), "sum": sum(data), "mean": mean(data), "median": median(data),
        "mode": mode(data), "min": min(data), "max": max(data), "range": max(data) - min(data),
        "std_dev (population)": std_dev(data, sample=False),
    }
    if len(data) > 1:
        out["std_dev (sample)"] = std_dev(data, sample=True)
    return out
