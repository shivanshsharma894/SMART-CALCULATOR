"""Turn numeric results into clean, human-friendly strings."""
import math


def format_number(value) -> str:
    """Format ints, floats and complex numbers for display."""
    if isinstance(value, complex):
        re, im = format_number(value.real), format_number(abs(value.imag))
        sign = "-" if value.imag < 0 else "+"
        return f"{re} {sign} {im}i"
    if isinstance(value, int):
        s = str(value)
        if len(s) > 40:  # very large integers -> scientific notation
            digits = s.lstrip("-")
            sign = "-" if s.startswith("-") else ""
            return f"{sign}{digits[0]}.{digits[1:11]}e+{len(digits) - 1}"
        return s
    if math.isnan(value) or math.isinf(value):
        return str(value)
    if abs(value) < 1e-12:
        return "0"
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.12g}"
