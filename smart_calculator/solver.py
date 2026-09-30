"""Equation solver: linear, quadratic, and systems of linear equations.

``solve_equation`` accepts text such as ``2x + 3 = 7`` or ``x^2 - 5x + 6 = 0``.
It reuses the safe evaluator: f(x) = lhs - rhs is sampled at a few points to
recover polynomial coefficients, then checked at extra points to confirm the
equation really is linear/quadratic.
"""
import math
from typing import List, Sequence, Tuple, Union

from .exceptions import CalculatorError, SolverError
from .formatting import format_number
from .functions import CONSTANTS, build_functions
from .parser import evaluate, free_variables, parse_expression

Number = Union[float, complex]
EPS = 1e-9


def solve_linear(a: float, b: float) -> List[float]:
    """Solve a*x + b = 0."""
    if abs(a) < EPS:
        raise SolverError("No solution" if abs(b) >= EPS else "Infinitely many solutions")
    return [-b / a]


def solve_quadratic(a: float, b: float, c: float) -> List[Number]:
    """Solve a*x^2 + b*x + c = 0 (real or complex roots)."""
    if abs(a) < EPS:
        return solve_linear(b, c)
    d = b * b - 4 * a * c
    if abs(d) < EPS:
        return [-b / (2 * a)]
    if d > 0:
        s = math.sqrt(d)
        return [(-b + s) / (2 * a), (-b - s) / (2 * a)]
    s = math.sqrt(-d)
    return [complex(-b / (2 * a), s / (2 * a)), complex(-b / (2 * a), -s / (2 * a))]


def solve_system(coeffs: Sequence[Sequence[float]], consts: Sequence[float]) -> List[float]:
    """Solve A·x = b using Gaussian elimination with partial pivoting."""
    n = len(coeffs)
    if n == 0 or len(consts) != n or any(len(row) != n for row in coeffs):
        raise SolverError("System must be square: n equations and n unknowns")
    m = [list(map(float, row)) + [float(consts[i])] for i, row in enumerate(coeffs)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < EPS:
            raise SolverError("System has no unique solution")
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for k in range(col, n + 1):
                m[r][k] -= factor * m[col][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))) / m[i][i]
    return x


def solve_equation(text: str) -> Tuple[str, List[Number]]:
    """Solve a one-variable linear or quadratic equation given as text."""
    if text.count("=") != 1:
        raise SolverError("Equation must contain exactly one '=' sign")
    lhs, rhs = (side.strip() for side in text.split("="))
    if not lhs or not rhs:
        raise SolverError("Both sides of the equation are required")
    try:
        node = parse_expression(f"({lhs}) - ({rhs})")
    except CalculatorError as exc:
        raise SolverError(str(exc))
    variables = free_variables(node) - set(CONSTANTS)
    if len(variables) != 1:
        raise SolverError("Equation must contain exactly one unknown variable")
    (var,) = variables
    funcs = build_functions("rad")

    def f(x):
        try:
            return float(evaluate(node, {**CONSTANTS, var: x}, funcs))
        except CalculatorError as exc:
            raise SolverError(str(exc))

    f0, f1, f2 = f(0), f(1), f(2)
    a = (f2 - 2 * f1 + f0) / 2
    b = f1 - f0 - a
    c = f0
    for x in (-3, 3.5, 7):  # verify the polynomial model
        if abs(a * x * x + b * x + c - f(x)) > 1e-7 * max(1, abs(f(x))):
            raise SolverError("Only linear and quadratic equations are supported")
    a, b, c = (round(v, 10) for v in (a, b, c))
    return var, solve_quadratic(a, b, c)


def format_root(value: Number) -> str:
    """Pretty-print a real or complex root."""
    if isinstance(value, complex):
        return format_number(complex(round(value.real, 10), round(value.imag, 10)))
    return format_number(round(value, 10))
