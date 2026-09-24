import unittest

from backend.services.benchmark import compare_timings, percentile


class BenchmarkTests(unittest.TestCase):
    def test_percentile_and_comparison_metrics(self):
        self.assertEqual(percentile([10.0, 20.0, 30.0, 40.0], 95), 38.5)

        metrics = compare_timings([100.0, 110.0, 90.0], [50.0, 55.0, 45.0])

        self.assertEqual(metrics["before_avg_ms"], 100.0)
        self.assertEqual(metrics["after_avg_ms"], 50.0)
        self.assertEqual(metrics["speedup"], 2.0)
        self.assertEqual(metrics["improvement_percentage"], 50.0)
        self.assertEqual(metrics["execution_count"], 3)


if __name__ == "__main__":
    unittest.main()