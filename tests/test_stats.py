import unittest

from smart_calculator import stats
from smart_calculator.exceptions import StatsError


class TestStats(unittest.TestCase):
    def test_measures(self):
        data = [2, 4, 4, 4, 5, 5, 7, 9]
        self.assertEqual(stats.mean(data), 5)
        self.assertEqual(stats.median(data), 4.5)
        self.assertEqual(stats.mode(data), [4])
        self.assertAlmostEqual(stats.std_dev(data, sample=False), 2)

    def test_mode_unique(self):
        self.assertEqual(stats.mode([1, 2, 3]), [])

    def test_parse(self):
        self.assertEqual(stats.parse_numbers("1, 2 3.5"), [1, 2, 3.5])
        for bad in ["", "a b", "nan"]:
            with self.assertRaises(StatsError):
                stats.parse_numbers(bad)

    def test_errors(self):
        with self.assertRaises(StatsError):
            stats.mean([])
        with self.assertRaises(StatsError):
            stats.variance([1])


if __name__ == "__main__":
    unittest.main()
