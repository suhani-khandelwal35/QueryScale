import unittest
from pathlib import Path


class SchemaTests(unittest.TestCase):
    def test_banking_tables_and_relationships_are_defined(self):
        schema = (Path(__file__).parents[1] / "database" / "schema.sql").read_text(encoding="utf-8")

        for table in ["Branches", "Customers", "Accounts", "Transactions", "Loans"]:
            self.assertIn(f"CREATE TABLE `{table}`", schema)

        relationships = [
            "REFERENCES `Branches` (`branch_id`)",
            "REFERENCES `Customers` (`customer_id`)",
            "REFERENCES `Accounts` (`account_id`)",
        ]
        for relationship in relationships:
            self.assertIn(relationship, schema)


if __name__ == "__main__":
    unittest.main()