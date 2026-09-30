"""Custom exception hierarchy so callers can handle failures precisely."""


class CalculatorError(Exception):
    """Base class for all errors raised by Smart Calculator."""


class ParseError(CalculatorError):
    """The input text is not a valid expression."""


class EvaluationError(CalculatorError):
    """A valid expression could not be evaluated (e.g. division by zero)."""


class UnitError(CalculatorError):
    """Unknown unit or invalid unit conversion."""


class SolverError(CalculatorError):
    """An equation or system could not be solved."""


class StatsError(CalculatorError):
    """Invalid input for a statistics operation."""


class HistoryError(CalculatorError):
    """History entry not found or history storage problem."""
