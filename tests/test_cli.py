import unittest

from smart_calculator import Calculator, History
from smart_calculator.cli import CalculatorCLI, QuitRequested


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.cli = CalculatorCLI(Calculator(history=History()))

    def test_expression(self):
        self.assertEqual(self.cli.handle("2+3*4"), "14")
        self.assertEqual(self.cli.handle("10/4"), "2.5")

    def test_errors_are_messages_not_crashes(self):
        self.assertTrue(self.cli.handle("1/0").startswith("Error"))
        self.assertTrue(self.cli.handle(":nope").startswith("Error"))
        self.assertEqual(self.cli.handle(""), "")

    def test_convert(self):
        self.assertEqual(self.cli.handle(":convert 100 c to f"), "100 c = 212 f")
        self.assertTrue(self.cli.handle(":convert abc").startswith("Error"))

    def test_solve_and_system(self):
        self.assertEqual(self.cli.handle(":solve 2x+3=7"), "x = 2")
        self.assertEqual(self.cli.handle(":system 2,1,5; 1,-1,1"), "x1 = 2\nx2 = 1")

    def test_stats(self):
        self.assertIn("mean", self.cli.handle(":stats 1 2 3"))

    def test_history_commands(self):
        self.cli.handle("1+1")
        self.assertIn("1+1 = 2", self.cli.handle(":history"))
        self.assertIn("1+1", self.cli.handle(":search 1+"))
        self.assertEqual(self.cli.handle(":delete 1"), "Deleted.")
        self.assertEqual(self.cli.handle(":history"), "(no entries)")

    def test_mode_vars(self):
        self.assertEqual(self.cli.handle(":mode rad"), "Angle mode: rad")
        self.cli.handle("x = 3")
        self.assertEqual(self.cli.handle(":vars"), "x = 3")

    def test_quit(self):
        with self.assertRaises(QuitRequested):
            self.cli.handle(":quit")


if __name__ == "__main__":
    unittest.main()
