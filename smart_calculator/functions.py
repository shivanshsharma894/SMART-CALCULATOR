"""Mathematical constants and the function table used by the evaluator."""
import math
from typing import Callable, Dict

CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "phi": (1 + math.sqrt(5)) / 2,
}


def _lcm(a, b):
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def build_functions(angle_mode: str = "deg") -> Dict[str, Callable]:
    """Build the function table. Trig functions honour ``angle_mode`` ('deg' or 'rad')."""
    deg = angle_mode == "deg"

    def to_rad(x):
        return math.radians(x) if deg else x

    def from_rad(x):
        return math.degrees(x) if deg else x

    def tan(x):
        r = to_rad(x)
        if abs(math.cos(r)) < 1e-12:
            raise ValueError("tan is undefined at this angle")
        return math.tan(r)

    def cbrt(x):
        return math.copysign(abs(x) ** (1 / 3), x)

    def log(x, base=10):
        return math.log(x, base)

    def round_(x, digits=0):
        return round(x, int(digits))

    def percent(x, p):
        return x * p / 100

    def avg(*xs):
        if not xs:
            raise ValueError("avg needs at least one value")
        return sum(xs) / len(xs)

    return {
        "sin": lambda x: math.sin(to_rad(x)),
        "cos": lambda x: math.cos(to_rad(x)),
        "tan": tan,
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "sqrt": math.sqrt, "cbrt": cbrt,
        "ln": math.log, "log": log, "log10": math.log10, "log2": math.log2,
        "exp": math.exp, "abs": abs, "round": round_,
        "floor": math.floor, "ceil": math.ceil,
        "factorial": math.factorial, "gcd": math.gcd, "lcm": getattr(math, "lcm", _lcm),
        "ncr": math.comb, "npr": math.perm,
        "hypot": math.hypot, "pow": math.pow,
        "deg": math.degrees, "rad": math.radians,
        "min": min, "max": max, "sum": lambda *xs: sum(xs), "avg": avg,
        "percent": percent,
    }
