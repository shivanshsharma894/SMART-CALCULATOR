"""Tokenizer, recursive-descent parser and *safe* evaluator.

No ``eval``/``exec`` is used, so user input can never run arbitrary code.

Grammar (lowest to highest precedence)::

    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | '//' | '%' | implicit) unary)*
    unary   := ('-' | '+') unary | power
    power   := postfix ('^' unary)?          # right associative
    postfix := primary '!'*
    primary := NUMBER | IDENT '(' args ')' | IDENT | '(' expr ')'
"""
import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set

from .exceptions import EvaluationError, ParseError

MAX_EXPR_LENGTH = 500
MAX_EXPONENT = 10_000
MAX_FACTORIAL = 1_000

_TOKEN_SPEC = [
    ("NUMBER", r"\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?"),
    ("IDENT", r"[A-Za-z_][A-Za-z_0-9]*"),
    ("FLOORDIV", r"//"),
    ("POW", r"\*\*|\^"),
    ("OP", r"[+\-*/%]"),
    ("FACT", r"!"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("SKIP", r"\s+"),
    ("MISMATCH", r"."),
]
_TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _TOKEN_SPEC))


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    pos: int


def tokenize(text: str) -> List[Token]:
    """Split text into tokens; raises ParseError on illegal characters."""
    if len(text) > MAX_EXPR_LENGTH:
        raise ParseError(f"Expression too long (max {MAX_EXPR_LENGTH} characters)")
    tokens = []
    for m in _TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind == "SKIP":
            continue
        if kind == "MISMATCH":
            raise ParseError(f"Unexpected character {m.group()!r} at position {m.start()}")
        tokens.append(Token(kind, m.group(), m.start()))
    tokens.append(Token("END", "", len(text)))
    return tokens


class Parser:
    """Builds an AST of nested tuples from a token list."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    @property
    def cur(self) -> Token:
        return self.tokens[self.i]

    def advance(self) -> Token:
        tok = self.cur
        if tok.kind != "END":
            self.i += 1
        return tok

    def expect(self, kind: str, what: str) -> Token:
        if self.cur.kind != kind:
            raise ParseError(f"Expected {what} at position {self.cur.pos}")
        return self.advance()

    def parse(self):
        if self.cur.kind == "END":
            raise ParseError("Empty expression")
        node = self.expr()
        if self.cur.kind != "END":
            raise ParseError(f"Unexpected token {self.cur.value!r} at position {self.cur.pos}")
        return node

    def expr(self):
        node = self.term()
        while self.cur.kind == "OP" and self.cur.value in ("+", "-"):
            op = self.advance().value
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while True:
            c = self.cur
            if (c.kind == "OP" and c.value in ("*", "/", "%")) or c.kind == "FLOORDIV":
                op = self.advance().value
                node = ("bin", op, node, self.unary())
            elif c.kind in ("IDENT", "LPAREN"):  # implicit multiplication: 2x, 3(4+1)
                node = ("bin", "*", node, self.unary())
            else:
                return node

    def unary(self):
        if self.cur.kind == "OP" and self.cur.value in ("+", "-"):
            op = self.advance().value
            return ("unary", op, self.unary())
        return self.power()

    def power(self):
        base = self.postfix()
        if self.cur.kind == "POW":
            self.advance()
            return ("bin", "^", base, self.unary())
        return base

    def postfix(self):
        node = self.primary()
        while self.cur.kind == "FACT":
            self.advance()
            node = ("fact", node)
        return node

    def primary(self):
        tok = self.cur
        if tok.kind == "NUMBER":
            self.advance()
            return ("num", int(tok.value) if tok.value.isdigit() else float(tok.value))
        if tok.kind == "IDENT":
            self.advance()
            if self.cur.kind == "LPAREN":
                self.advance()
                args = []
                if self.cur.kind != "RPAREN":
                    args.append(self.expr())
                    while self.cur.kind == "COMMA":
                        self.advance()
                        args.append(self.expr())
                self.expect("RPAREN", "')' after function arguments")
                return ("call", tok.value.lower(), args)
            return ("var", tok.value.lower())
        if tok.kind == "LPAREN":
            self.advance()
            node = self.expr()
            self.expect("RPAREN", "')'")
            return node
        raise ParseError(f"Unexpected {tok.value or 'end of input'!r} at position {tok.pos}")


def parse_expression(text: str):
    """Parse text into an AST."""
    try:
        return Parser(tokenize(text)).parse()
    except RecursionError:
        raise ParseError("Expression is nested too deeply")


def free_variables(node) -> Set[str]:
    """Names of variables referenced in an AST (function names excluded)."""
    kind = node[0]
    if kind == "var":
        return {node[1]}
    if kind == "unary":
        return free_variables(node[2])
    if kind == "fact":
        return free_variables(node[1])
    if kind == "bin":
        return free_variables(node[2]) | free_variables(node[3])
    if kind == "call":
        out: Set[str] = set()
        for a in node[2]:
            out |= free_variables(a)
        return out
    return set()


def _power(base, exp):
    if abs(exp) > MAX_EXPONENT:
        raise EvaluationError("Exponent too large")
    if base == 0 and exp < 0:
        raise EvaluationError("Division by zero")
    try:
        result = base ** exp
    except OverflowError:
        raise EvaluationError("Result too large")
    if isinstance(result, complex):
        raise EvaluationError("Result is a complex number (not supported here)")
    return result


def _factorial(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if not isinstance(v, int) or v < 0:
        raise EvaluationError("Factorial needs a non-negative integer")
    if v > MAX_FACTORIAL:
        raise EvaluationError(f"Factorial input too large (max {MAX_FACTORIAL})")
    return math.factorial(v)


def _binary(op, l, r):
    try:
        if op == "+":
            return l + r
        if op == "-":
            return l - r
        if op == "*":
            return l * r
        if op in ("/", "//", "%") and r == 0:
            raise EvaluationError("Division by zero")
        if op == "/":
            return l / r
        if op == "//":
            return l // r
        if op == "%":
            return l % r
        if op == "^":
            return _power(l, r)
    except OverflowError:
        raise EvaluationError("Result too large")
    raise EvaluationError(f"Unknown operator {op!r}")


def evaluate(node, variables: Dict[str, Any], functions: Dict[str, Callable]):
    """Evaluate an AST with the given variables and function table."""
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "var":
        if node[1] in variables:
            return variables[node[1]]
        raise EvaluationError(f"Unknown variable '{node[1]}'")
    if kind == "unary":
        v = evaluate(node[2], variables, functions)
        return -v if node[1] == "-" else v
    if kind == "fact":
        return _factorial(evaluate(node[1], variables, functions))
    if kind == "bin":
        return _binary(node[1], evaluate(node[2], variables, functions),
                       evaluate(node[3], variables, functions))
    if kind == "call":
        fn = functions.get(node[1])
        if fn is None:
            raise EvaluationError(f"Unknown function '{node[1]}'")
        args = [evaluate(a, variables, functions) for a in node[2]]
        try:
            result = fn(*args)
        except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
            raise EvaluationError(f"{node[1]}(): {exc}")
        if isinstance(result, complex):
            raise EvaluationError(f"{node[1]}(): complex result not supported")
        return result
    raise EvaluationError("Malformed expression")


def evaluate_expression(text: str, variables: Optional[Dict[str, Any]] = None,
                        functions: Optional[Dict[str, Callable]] = None):
    """Parse and evaluate ``text`` in one step."""
    from .functions import build_functions
    try:
        return evaluate(parse_expression(text), variables or {}, functions or build_functions())
    except RecursionError:
        raise EvaluationError("Expression is nested too deeply")
