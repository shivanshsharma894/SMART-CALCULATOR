import unittest

from smart_calculator.exceptions import UnitError
from smart_calculator.units import convert


class TestUnits(unittest.TestCase):
    def test_linear(self):
        self.assertAlmostEqual(convert(1, "km", "m"), 1000)
        self.assertAlmostEqual(convert(1, "mi", "km"), 1.609344)
        self.assertAlmostEqual(convert(1, "GB", "MB"), 1024)
        self.assertAlmostEqual(convert(36, "km/h", "m/s"), 10)

    def test_temperature(self):
        self.assertAlmostEqual(convert(100, "c", "f"), 212)
        self.assertAlmostEqual(convert(32, "f", "c"), 0)
        self.assertAlmostEqual(convert(0, "c", "k"), 273.15)

    def test_errors(self):
        with self.assertRaises(UnitError):
            convert(1, "kg", "m")
        with self.assertRaises(UnitError):
            convert(1, "parsec", "m")
        with self.assertRaises(UnitError):
            convert(-300, "c", "f")
        with self.assertRaises(UnitError):
            convert(float("inf"), "m", "km")


if __name__ == "__main__":
    unittest.main()
