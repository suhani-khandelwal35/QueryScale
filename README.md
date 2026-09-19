# QueryScale

QueryScale is an intelligent database performance optimization system for banking workloads.

## Project scope

This repository currently contains the database foundation for Person A's work, including:

- MySQL schema definition
- environment configuration template
- dependency manifest

## Database setup

1. Create a MySQL database server and update the values in `.env` based on `.env.example`.
2. Run the schema script:

```bash
mysql --host "$DB_HOST" --port "$DB_PORT" --user "$DB_USER" --password="$DB_PASSWORD" < database/schema.sql
```

3. Confirm the `queryscale` database contains the required banking tables.

## Synthetic data generation

Generate the default dataset in MySQL:

```bash
python scripts/seed.py
```

You can also override the defaults with arguments such as:

```bash
python scripts/seed.py --branches 50 --customers 10000 --accounts 15000 --transactions 100000 --loans 5000
```

## Workload execution and performance logging

Execute the baseline banking workload and capture real timing measurements in `data/query_logs.csv`:

```bash
python scripts/workload.py --iterations 100
```

Optional controls:

```bash
python scripts/workload.py --list-queries
python scripts/workload.py --dry-run --iterations 5
```

The script records the following fields for each query execution:

- `query_id`
- `query_template`
- `timestamp`
- `execution_time_ms`
- `frequency`
- `tables`
- `where_columns`
- `join_columns`
- `order_columns`

## Repository structure

```text
QueryScale/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── database/
│   ├── README.md
│   ├── queries.sql
│   └── schema.sql
├── data/
│   └── query_logs.csv
└── scripts/
    ├── seed.py
    └── workload.py
```

## Notes

This is the initial foundation for the QueryScale optimization pipeline. Additional modules for synthetic data generation, workload generation, analysis, and recommendation will be added in later milestones.
