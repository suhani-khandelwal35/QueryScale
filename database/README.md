# Database layer

This directory contains the core MySQL schema for QueryScale.

## Schema

The `queryscale` database includes the following tables:

- `Branches`
- `Customers`
- `Accounts`
- `Transactions`
- `Loans`

These tables model a simplified banking workload with the expected referential relationships:

- `Branches` -> `Customers` -> `Accounts` -> `Transactions`
- `Customers` -> `Loans`

## Usage

To initialize the database from the schema:

```bash
mysql --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --password="$DB_PASSWORD" < database/schema.sql
```

The script creates the database if it does not exist and applies the required foreign key relationships and table constraints.
