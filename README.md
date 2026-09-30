# SMART-CALCULATOR

A modular command-line **smart calculator** written in Python. It goes beyond `+ − × ÷`: it parses expressions safely (no `eval`), remembers variables and history, converts units, solves equations and computes statistics.

> Built for the **VITyarthi – Build Your Own Project** course evaluation.

## Overview
Most basic calculators can't handle full expressions, keep a history, or solve equations. Smart Calculator provides one tool for everyday math, unit conversion, algebra and statistics, with clear error messages and no external dependencies.

## Features
| Module | What it does |
|---|---|
| **Expression engine** | Operator precedence, parentheses, `^`, `%`, `//`, factorial `!`, implicit multiplication (`2x`), 35+ functions (trig, log, `ncr`, `percent`…), constants (`pi`, `e`…), variables (`x = 5`), `ans`, degree/radian modes |
| **Unit converter** | Length, mass, time, data, volume, speed, area, temperature |
| **Equation solver** | Linear & quadratic equations from text (`x^2-5x+6=0`, complex roots too) and n×n linear systems |
| **Statistics** | count, sum, mean, median, mode, min/max/range, population & sample std-dev |
| **History (CRUD)** | Persistent JSON history: view, search, delete, clear |
| **Logging & safety** | Rotating log file, custom exceptions, input-length/exponent/factorial limits |

## Technologies
Python 3.9+ (standard library only), `unittest`, Git/GitHub, GitHub Actions (CI).

## Project structure
```
smart-calculator/
├── main.py                  # entry point
├── smart_calculator/
│   ├── cli.py               # REPL + command routing
│   ├── engine.py            # Calculator class (variables, ans, modes)
│   ├── parser.py            # tokenizer, recursive-descent parser, safe evaluator
│   ├── functions.py         # constants + function table
│   ├── units.py             # unit converter
│   ├── solver.py            # equation / system solver
│   ├── stats.py             # statistics
│   ├── history.py           # history CRUD + JSON persistence
│   ├── formatting.py        # result formatting
│   ├── exceptions.py        # custom errors
│   └── logger.py            # logging setup
├── tests/                   # 38 unit tests
├── docs/                    # design diagrams & report guide
├── statement.md
└── .github/workflows/tests.yml
```

## Install & run
```bash
git clone https://github.com/<your-username>/smart-calculator.git
cd smart-calculator
python main.py                 # interactive mode
python main.py "2+3*4"         # one-shot mode
python main.py --mode rad "sin(pi/2)"
```
No `pip install` needed. Options: `--mode deg|rad`, `--no-save`, `--history-file PATH`, `--log-level LEVEL`.

## Usage examples
```
calc> 2+3*4
14
calc> x = 5
5
calc> 2x^2 + 1
51
calc> percent(200, 15)
30
calc> :convert 10 km to mi
10 km = 6.21371192237 mi
calc> :solve x^2 - 5x + 6 = 0
x = 3
x = 2
calc> :system 2,1,5; 1,-1,1
x1 = 2
x2 = 1
calc> :stats 4 8 15 16 23 42
calc> :history 5
```
Type `:help` inside the app for all commands.

## Testing
```bash
python -m unittest discover -s tests -v
```
Tests cover parsing, evaluation errors, security (no code execution), history persistence/corruption, unit conversion, solver edge cases, statistics and CLI behaviour.


## Made by

-Name:-Shivansh Sharma

-Registration number:-26MIM10224
