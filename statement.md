# Project Statement – Smart Calculator

## Problem statement
Students and everyday users often need more than a basic calculator: they want to type a whole expression, reuse earlier results, convert units, solve simple equations and summarise data. Doing this normally requires several different tools, and many quick scripts use Python's `eval`, which is unsafe. There is a need for one lightweight, safe, well-tested tool that combines these tasks with clear error messages.

## Scope
**In scope:** expression evaluation with variables/functions, unit conversion, linear & quadratic equation solving, linear systems, descriptive statistics, persistent history, logging, command-line interface.
**Out of scope:** graphing, symbolic algebra (e.g. simplification, calculus), equations above degree 2, GUI/web front-end (listed as future enhancements).

## Target users
- Students (school/college) doing maths, science and engineering homework
- Programmers and analysts who want a fast terminal calculator
- Anyone who wants a safe calculator with history

## High-level features
1. Safe expression engine (precedence, functions, variables, `ans`, deg/rad)
2. Unit converter (8 categories)
3. Equation & linear-system solver
4. Statistics summary
5. History with view / search / delete / clear, saved to JSON
6. Logging and robust error handling
