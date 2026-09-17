import unittest
from datetime import date

from backend.services.hierarchy_performance_service import _calculate_overall, _competition_rank, evaluation_window_open


class PerformanceRulesTests(unittest.TestCase):
    def test_weighting(self):
        self.assertEqual(_calculate_overall(80, 100, 100), 88.0)

    def test_competition_rank(self):
        self.assertEqual(_competition_rank([100, 95, 95, 80]), [1, 2, 2, 4])

    def test_evaluation_window(self):
        self.assertTrue(evaluation_window_open(date(2026, 9, 1), date(2026, 9, 25)))
        self.assertFalse(evaluation_window_open(date(2026, 9, 1), date(2026, 9, 24)))
        self.assertFalse(evaluation_window_open(date(2026, 9, 1), date(2026, 10, 1)))


if __name__ == "__main__":
    unittest.main()
