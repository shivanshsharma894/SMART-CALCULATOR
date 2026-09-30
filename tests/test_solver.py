import unittest

from smart_calculator.exceptions import SolverError
from smart_calculator.solver import solve_equation, solve_linear, solve_quadratic, solve_system


class TestSolver(unittest.TestCase):
    def test_linear(self):
        self.assertEqual(solve_linear(2, -4), [2])
        with self.assertRaises(SolverError):
            solve_linear(0, 5)

    def test_quadratic_roots(self):
        self.assertEqual(sorted(solve_quadratic(1, -5, 6)), [2, 3])
        self.assertEqual(solve_quadratic(1, -2, 1), [1])
        roots = solve_quadratic(1, 0, 1)
        self.assertEqual(roots[0], 1j)

    def test_system(self):
        x, y = solve_system([[2, 1], [1, -1]], [5, 1])
        self.assertAlmostEqual(x, 2)
        self.assertAlmostEqual(y, 1)
        with self.assertRaises(SolverError):
            solve_system([[1, 2], [2, 4]], [3, 6])
        with self.assertRaises(SolverError):
            solve_system([[1, 2]], [3])

    def test_solve_equation_text(self):
        var, roots = solve_equation("2x + 3 = 7")
        self.assertEqual(var, "x")
        self.assertAlmostEqual(roots[0], 2)
        _, roots = solve_equation("x^2 - 5x + 6 = 0")
        self.assertEqual(sorted(round(r, 6) for r in roots), [2, 3])

    def test_solve_equation_errors(self):
        for bad in ["2x+3", "x+y=3", "x^3=8", "5=5", "=3", "1/x=2"]:
            with self.assertRaises(SolverError, msg=bad):
                solve_equation(bad)


if __name__ == "__main__":
    unittest.main()
