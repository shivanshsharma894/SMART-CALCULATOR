import json
import tempfile
import unittest
from pathlib import Path

from smart_calculator.exceptions import HistoryError
from smart_calculator.history import History


class TestHistory(unittest.TestCase):
    def test_crud(self):
        h = History()
        e = h.add("1+1", "2")
        h.add("2*3", "6")
        self.assertEqual(h.get(e.id).result, "2")
        self.assertEqual(len(h.search("2*")), 1)
        h.delete(e.id)
        self.assertEqual(len(h), 1)
        with self.assertRaises(HistoryError):
            h.get(e.id)
        h.clear()
        self.assertEqual(len(h), 0)

    def test_max_entries(self):
        h = History(max_entries=3)
        for i in range(5):
            h.add(str(i), str(i))
        self.assertEqual([e.expression for e in h.all()], ["2", "3", "4"])

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "h.json"
            History(path).add("1+1", "2")
            again = History(path)
            self.assertEqual(len(again), 1)
            self.assertEqual(again.add("x", "y").id, 2)

    def test_corrupt_file_is_survived(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "h.json"
            path.write_text("{not json")
            self.assertEqual(len(History(path)), 0)


if __name__ == "__main__":
    unittest.main()
