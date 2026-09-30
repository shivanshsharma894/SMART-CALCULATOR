"""Logging setup.

The package logs to a NullHandler by default (library best practice).
The CLI calls ``configure_logging`` to write a rotating log file.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT_NAME = "smart_calculator"
DATA_DIR = Path(os.environ.get("SMART_CALC_HOME", Path.home() / ".smart_calculator"))

logging.getLogger(ROOT_NAME).addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    """Return a child logger such as ``smart_calculator.engine``."""
    return logging.getLogger(f"{ROOT_NAME}.{name}")


def configure_logging(level: str = "INFO", log_dir: Path = DATA_DIR) -> Path:
    """Attach a rotating file handler. Returns the log file path.

    Failure to create the log file never crashes the app.
    """
    root = logging.getLogger(ROOT_NAME)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    log_file = Path(log_dir) / "calculator.log"
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(log_file, maxBytes=200_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        root.addHandler(handler)
    except OSError:
        root.warning("Could not create log file at %s", log_file)
    return log_file
