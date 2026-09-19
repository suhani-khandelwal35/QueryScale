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

## Repository structure

```text
QueryScale/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── database/
│   ├── README.md
│   └── schema.sql
└── scripts/
```

## Notes

This is the initial foundation for the QueryScale optimization pipeline. Additional modules for synthetic data generation, workload generation, analysis, and recommendation will be added in later milestones.
