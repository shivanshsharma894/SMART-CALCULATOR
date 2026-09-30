"""Smart Calculator - expression evaluation, unit conversion, equation solving and statistics."""
from .engine import Calculator
from .history import History

__version__ = "1.0.0"
__all__ = ["Calculator", "History", "__version__"]
