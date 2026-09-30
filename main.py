"""Entry point:  python main.py            (interactive)
                python main.py "2+3*4"     (one-shot)"""
import sys

from smart_calculator.cli import main

if __name__ == "__main__":
    sys.exit(main())
