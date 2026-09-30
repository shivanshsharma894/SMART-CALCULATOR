"""Calculator engine: evaluates expressions with variables, ``ans`` and angle modes."""
import re
from typing import Dict, Optional

from .exceptions import CalculatorError, EvaluationError, ParseError
from .formatting import format_number
from .functions import CONSTANTS, build_functions
from .history import History
from .logger import get_logger
from .parser import evaluate_expression

log = get_logger("engine")
_ASSIGN_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.+)$")


class Calculator:
    """Stateful calculator. Supports ``x = 5`` assignments and the ``ans`` variable."""

    def __init__(self, angle_mode: str = "deg", history: Optional[History] = None):
        self.angle_mode = "deg"
        self.set_angle_mode(angle_mode)
        self.variables: Dict[str, float] = {}
        self.last_result = 0
        self.history = history if history is not None else History()

    def set_angle_mode(self, mode: str) -> None:
        mode = mode.lower()
        if mode not in ("deg", "rad"):
            raise CalculatorError("Angle mode must be 'deg' or 'rad'")
        self.angle_mode = mode
        self._functions = build_functions(mode)

    def _namespace(self) -> Dict[str, float]:
        ns = dict(CONSTANTS)
        ns.update(self.variables)
        ns["ans"] = self.last_result
        return ns

    def calculate(self, expression: str):
        """Evaluate ``expression`` and return the numeric result."""
        if not isinstance(expression, str) or not expression.strip():
            raise ParseError("Empty expression")
        try:
            match = _ASSIGN_RE.match(expression)
            if match:
                name, body = match.group(1).lower(), match.group(2)
                if name in CONSTANTS or name in self._functions or name == "ans":
                    raise EvaluationError(f"'{name}' is reserved and cannot be reassigned")
                value = evaluate_expression(body, self._namespace(), self._functions)
                self.variables[name] = value
            else:
                value = evaluate_expression(expression, self._namespace(), self._functions)
        except CalculatorError as exc:
            log.warning("Failed '%s': %s", expression.strip(), exc)
            raise
        self.last_result = value
        self.history.add(expression.strip(), format_number(value))
        log.info("Calculated '%s' = %s", expression.strip(), value)
        return value
