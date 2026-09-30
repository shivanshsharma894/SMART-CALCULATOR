"""Command-line interface: interactive REPL and one-shot mode."""
import argparse
import re
import sys
from typing import List, Optional

from . import solver, stats, units
from .engine import Calculator
from .exceptions import CalculatorError
from .formatting import format_number
from .history import History
from .logger import DATA_DIR, configure_logging, get_logger

log = get_logger("cli")

HELP = """Smart Calculator - type an expression or a :command

Expressions   2+3*4   sqrt(16)   2^10   5!   sin(30)   x = 5   2x+1   ans*2   percent(200,15)
Commands
  :convert 10 km to mi      convert units (:units lists them)
  :solve 2x+3=7             solve linear / quadratic equations
  :system 2,1,5; 1,-1,1     solve linear system (last number of each row = constant)
  :stats 4 8 15 16 23 42    descriptive statistics
  :mode [deg|rad]           show / set angle mode
  :vars                     show stored variables
  :history [n]              show last n calculations   :search TEXT   :delete ID   :clear
  :help                     this message              :quit         exit
"""


class QuitRequested(Exception):
    """Raised by :quit to leave the REPL."""


class CalculatorCLI:
    """Routes a line of user input to the right module and returns text output."""

    def __init__(self, calculator: Calculator):
        self.calc = calculator

    def handle(self, line: str) -> str:
        line = line.strip()
        if not line:
            return ""
        try:
            if line.startswith(":"):
                return self._command(line[1:])
            return format_number(self.calc.calculate(line))
        except QuitRequested:
            raise
        except CalculatorError as exc:
            return f"Error: {exc}"
        except Exception:  # last-resort guard so the REPL never crashes
            log.exception("Unexpected error for input %r", line)
            return "Error: unexpected problem (details written to the log file)"

    def _command(self, text: str) -> str:
        parts = text.split(None, 1)
        if not parts:
            return HELP
        name, arg = parts[0].lower(), (parts[1] if len(parts) > 1 else "")
        handler = getattr(self, f"_cmd_{name}", None)
        if handler is None:
            return f"Error: unknown command ':{name}'. Type :help"
        return handler(arg)

    # --- commands -------------------------------------------------
    def _cmd_help(self, arg):
        return HELP

    def _cmd_quit(self, arg):
        raise QuitRequested

    _cmd_exit = _cmd_quit

    def _cmd_convert(self, arg):
        m = re.match(r"^\s*(\S+)\s+(\S+)\s+(?:to|in)\s+(\S+)\s*$", arg, re.I)
        if not m:
            raise CalculatorError("Usage: :convert <value> <from> to <to>   e.g. :convert 10 km to mi")
        try:
            value = float(m.group(1))
        except ValueError:
            raise CalculatorError(f"'{m.group(1)}' is not a number")
        result = units.convert(value, m.group(2), m.group(3))
        return f"{format_number(value)} {m.group(2)} = {format_number(result)} {m.group(3)}"

    def _cmd_units(self, arg):
        return "\n".join(f"{cat:12}{', '.join(names)}" for cat, names in units.list_units().items())

    def _cmd_solve(self, arg):
        var, roots = solver.solve_equation(arg)
        return "\n".join(f"{var} = {solver.format_root(r)}" for r in roots)

    def _cmd_system(self, arg):
        rows = [stats.parse_numbers(r) for r in arg.split(";") if r.strip()]
        if not rows or any(len(r) != len(rows) + 1 for r in rows):
            raise CalculatorError("Give n rows of n coefficients plus a constant, e.g. :system 2,1,5; 1,-1,1")
        sol = solver.solve_system([r[:-1] for r in rows], [r[-1] for r in rows])
        return "\n".join(f"x{i + 1} = {format_number(round(v, 10))}" for i, v in enumerate(sol))

    def _cmd_stats(self, arg):
        summary = stats.describe(stats.parse_numbers(arg))
        lines = []
        for k, v in summary.items():
            shown = ", ".join(format_number(x) for x in v) or "none" if isinstance(v, list) else format_number(v)
            lines.append(f"{k:22}{shown}")
        return "\n".join(lines)

    def _cmd_mode(self, arg):
        if arg.strip():
            self.calc.set_angle_mode(arg.strip())
        return f"Angle mode: {self.calc.angle_mode}"

    def _cmd_vars(self, arg):
        if not self.calc.variables:
            return "No variables defined (try: x = 5)"
        return "\n".join(f"{k} = {format_number(v)}" for k, v in sorted(self.calc.variables.items()))

    def _cmd_history(self, arg):
        try:
            limit = int(arg) if arg.strip() else 10
        except ValueError:
            raise CalculatorError("Usage: :history [count]")
        return self._show(self.calc.history.all(limit))

    def _cmd_search(self, arg):
        return self._show(self.calc.history.search(arg.strip()))

    def _cmd_delete(self, arg):
        try:
            self.calc.history.delete(int(arg))
        except ValueError:
            raise CalculatorError("Usage: :delete <id>")
        return "Deleted."

    def _cmd_clear(self, arg):
        self.calc.history.clear()
        return "History cleared."

    @staticmethod
    def _show(entries) -> str:
        return "\n".join(f"#{e.id:<4}{e.expression} = {e.result}" for e in entries) or "(no entries)"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="smart-calculator", description="Smart Calculator")
    p.add_argument("expression", nargs="*", help="evaluate once and exit (omit for interactive mode)")
    p.add_argument("--mode", choices=["deg", "rad"], default="deg", help="angle mode (default: deg)")
    p.add_argument("--no-save", action="store_true", help="do not persist history to disk")
    p.add_argument("--history-file", default=str(DATA_DIR / "history.json"))
    p.add_argument("--log-level", default="INFO")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level)
    history = History(None if args.no_save else args.history_file)
    cli = CalculatorCLI(Calculator(args.mode, history))

    if args.expression:
        out = cli.handle(" ".join(args.expression))
        print(out)
        return 1 if out.startswith("Error") else 0

    print("Smart Calculator 1.0 - type :help for help, :quit to exit")
    while True:
        try:
            line = input("calc> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        try:
            out = cli.handle(line)
        except QuitRequested:
            return 0
        if out:
            print(out)


if __name__ == "__main__":
    sys.exit(main())
