import unittest

from backend.services.query_analyzer import analyze_query


class QueryAnalyzerTests(unittest.TestCase):
    def test_basic_account_lookup(self):
        query = """
            SELECT *
            FROM Transactions
            WHERE account_id = 101
            ORDER BY txn_date DESC;
        """
        result = analyze_query(query)
        self.assertEqual(result["tables"], ["Transactions"])
        self.assertEqual(result["where_columns"], ["account_id"])
        self.assertEqual(result["join_columns"], [])
        self.assertEqual(result["order_columns"], ["txn_date"])

    def test_customer_join_query(self):
        query = """
            SELECT c.name, a.account_id
            FROM Customers c
            JOIN Accounts a
            ON c.customer_id = a.customer_id
            WHERE c.customer_id = 42;
        """
        result = analyze_query(query)
        self.assertEqual(result["tables"], ["Customers", "Accounts"])
        self.assertEqual(result["where_columns"], ["customer_id"])
        self.assertEqual(result["join_columns"], ["customer_id"])
        self.assertEqual(result["order_columns"], [])

    def test_date_range_query(self):
        query = """
            SELECT *
            FROM Transactions
            WHERE txn_date BETWEEN '2024-01-01' AND '2024-12-31';
        """
        result = analyze_query(query)
        self.assertEqual(result["tables"], ["Transactions"])
        self.assertEqual(result["where_columns"], ["txn_date"])


if __name__ == "__main__":
    unittest.main()
