import unittest

from smart_calculator.exceptions import EvaluationError, ParseError
from smart_calculator.parser import evaluate_expression as ev


class TestParser(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(ev("2+3*4"), 14)
        self.assertEqual(ev("(2+3)*4"), 20)

    def test_power_right_associative_and_unary(self):
        self.assertEqual(ev("2^3^2"), 512)
        self.assertEqual(ev("-2^2"), -4)
        self.assertEqual(ev("2^-1"), 0.5)

    def test_operators(self):
        self.assertEqual(ev("7//2"), 3)
        self.assertEqual(ev("7%4"), 3)
        self.assertEqual(ev("10/4"), 2.5)
        self.assertEqual(ev("5!"), 120)

    def test_implicit_multiplication(self):
        self.assertEqual(ev("2x", {"x": 4}), 8)
        self.assertEqual(ev("3(4+1)"), 15)

    def test_functions(self):
        self.assertEqual(ev("max(1,5,3)"), 5)
        self.assertAlmostEqual(ev("sqrt(2)^2"), 2)

    def test_errors(self):
        for bad in ["", "2+", "(2+3", "2 $ 3", "2 3"]:
            with self.assertRaises(ParseError, msg=bad):
                ev(bad)
        with self.assertRaises(EvaluationError):
            ev("1/0")
        with self.assertRaises(EvaluationError):
            ev("foo(1)")
        with self.assertRaises(EvaluationError):
            ev("sqrt(-1)")
        with self.assertRaises(EvaluationError):
            ev("(-8)^0.5")
        with self.assertRaises(EvaluationError):
            ev("10^100000")
        with self.assertRaises(EvaluationError):
            ev("y+1")

    def test_no_code_execution(self):
        with self.assertRaises(ParseError):
            ev("__import__('os').system('echo hi')")

    def test_length_limit(self):
        with self.assertRaises(ParseError):
            ev("1+" * 400 + "1")


if __name__ == "__main__":
    unittest.main()
