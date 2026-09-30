import math
import unittest

from smart_calculator import Calculator, History
from smart_calculator.exceptions import CalculatorError, EvaluationError


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator(history=History())

    def test_basic_and_ans(self):
        self.assertEqual(self.calc.calculate("2+3"), 5)
        self.assertEqual(self.calc.calculate("ans*2"), 10)

    def test_variables(self):
        self.calc.calculate("x = 5")
        self.assertEqual(self.calc.calculate("x^2 + 1"), 26)

    def test_reserved_names(self):
        for bad in ("pi = 3", "sin = 2", "ans = 1"):
            with self.assertRaises(EvaluationError):
                self.calc.calculate(bad)

    def test_angle_modes(self):
        self.assertAlmostEqual(self.calc.calculate("sin(30)"), 0.5)
        self.calc.set_angle_mode("rad")
        self.assertAlmostEqual(self.calc.calculate("sin(pi/2)"), 1)
        with self.assertRaises(CalculatorError):
            self.calc.set_angle_mode("grad")

    def test_history_recorded_only_on_success(self):
        self.calc.calculate("1+1")
        with self.assertRaises(CalculatorError):
            self.calc.calculate("1/0")
        self.assertEqual(len(self.calc.history), 1)

    def test_functions(self):
        self.assertEqual(self.calc.calculate("percent(200,15)"), 30)
        self.assertEqual(self.calc.calculate("ncr(5,2)"), 10)
        self.assertEqual(self.calc.calculate("gcd(12,18)"), 6)
        self.assertAlmostEqual(self.calc.calculate("cbrt(-27)"), -3)
        with self.assertRaises(EvaluationError):
            self.calc.calculate("tan(90)")


if __name__ == "__main__":
    unittest.main()
