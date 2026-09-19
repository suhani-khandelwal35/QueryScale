-- QueryScale baseline banking workload
-- Person A: workload definition and query templates for performance profiling

-- Q001 - Account transactions
SELECT *
FROM Transactions
WHERE account_id = ?;

-- Q002 - Transaction date range
SELECT *
FROM Transactions
WHERE txn_date BETWEEN ? AND ?;

-- Q003 - Account transaction history
SELECT *
FROM Transactions
WHERE account_id = ?
ORDER BY txn_date DESC;

-- Q004 - Customer account lookup
SELECT c.name, a.account_id
FROM Customers c
JOIN Accounts a
ON c.customer_id = a.customer_id
WHERE c.customer_id = ?;

-- Q005 - Customer loans
SELECT *
FROM Loans
WHERE customer_id = ?;

-- Q006 - Branch customer history
SELECT *
FROM Customers
WHERE branch_id = ?;

-- Q007 - Monthly transaction summary
SELECT DATE_FORMAT(txn_date, '%Y-%m') AS month,
       COUNT(*) AS txn_count,
       SUM(amount) AS txn_total
FROM Transactions
WHERE txn_date BETWEEN ? AND ?
GROUP BY DATE_FORMAT(txn_date, '%Y-%m')
ORDER BY month;
