import csv
import tempfile
import unittest
from pathlib import Path

from backend.services.candidate_generator import generate_candidates


class CandidateGeneratorTests(unittest.TestCase):
    def test_generate_candidates_recommends_high_value_indexes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_path = Path(tmpdir) / "candidate_features.csv"
            output_path = Path(tmpdir) / "index_candidates.csv"

            with feature_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow([
                    "candidate_id",
                    "table",
                    "columns",
                    "frequency",
                    "average_execution_time",
                    "where_usage",
                    "join_usage",
                    "order_usage",
                    "table_size",
                    "existing_index",
                ])
                writer.writerow([
                    "IDX_TRANSACTIONS_account_id",
                    "Transactions",
                    "account_id",
                    "3",
                    "27.5",
                    "1",
                    "0",
                    "1",
                    "100000",
                    "false",
                ])
                writer.writerow([
                    "IDX_CUSTOMERS_customer_id",
                    "Customers",
                    "customer_id",
                    "1",
                    "5.0",
                    "1",
                    "0",
                    "0",
                    "10000",
                    "true",
                ])

            rows = generate_candidates(feature_path, output_path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["candidate_id"], "IDX_TRANSACTIONS_account_id")
            self.assertIn("CREATE INDEX", rows[0]["recommended_action"])
            self.assertGreater(rows[0]["score"], 0)


if __name__ == "__main__":
    unittest.main()
