# Assessment Data Generator

Small utility to generate sample e‑commerce data (customers, products, orders, order items) into a PostgreSQL database and write CSV exports to `csv_output/`.

This repository contains:

- `data_generator.py` — main script that creates fake customers, products, orders and order items and writes CSVs. Uses Pydantic models for validation.
- `models.py` — SQLAlchemy models representing the DB schema.
- `create_schema.py` — script to create the required tables and indexes using SQLAlchemy models (replaces `init.sql`).
- `db_utils.py` — small DB helper functions (bulk insert/update, CSV writer) used by the generator.
- `requirements.txt` — Python dependencies.
- `run.sh` — convenience wrapper to start Postgres, create the schema and run the generator.
- `docker-compose.yml` — optional local Postgres service for quick testing.
- `csv_output/` — output CSV files produced by the script.

Note: `init.sql` is kept for historical/reference purposes only; schema creation is now done in Python via `models.py` + `create_schema.py`.

Quick plan / checklist

1. Install dependencies
2. Provide Postgres credentials via environment variables (or run Postgres via `docker-compose`)
3. Initialize DB schema (`python create_schema.py`)
4. Run the generator (`python data_generator.py` or `./run.sh`)
5. Inspect CSVs in `csv_output/`

Requirements

- Python 3.8+
- PostgreSQL (local or remote)
- pip

Install Python deps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies of note in `requirements.txt`:

- `psycopg2-binary` — Postgres driver
- `faker` — data generation
- `python-dotenv` — load .env files
- `pydantic` — runtime data validation
- `sqlalchemy` — models and schema creation

Environment variables

The scripts read Postgres connection settings from environment variables. Create a `.env` file or export them in your shell:

- POSTGRES_HOST (e.g., localhost)
- POSTGRES_PORT (e.g., 5432)
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

Example `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=assessment_db
```

Initialize the database schema

Create the database (if missing) and then run the SQLAlchemy-based creator. This will create tables and indexes if they do not already exist:

```bash
python create_schema.py
```

If you prefer Docker Compose, start the Postgres service first, then run the schema creator:

```bash
docker-compose up -d
python create_schema.py
```

Run the generator

Make sure the environment variables are set and then run:

```bash
python data_generator.py
```

Or use the wrapper (which starts the DB, creates the schema, then runs the generator):

```bash
./run.sh
```

Logging

By default `data_generator.py` logs to the console (stderr) with timestamps and stack traces on errors. For short runs this is usually sufficient. To persist logs to disk, add a `RotatingFileHandler` (example in the notes below) or enable a custom logging configuration.

What the scripts do

- `create_schema.py`: reads DB connection from environment variables and runs `Base.metadata.create_all(engine)` using the SQLAlchemy models in `models.py`.
- `data_generator.py`: generates fake customers/products/orders/order_items, validates rows with Pydantic models, uses `db_utils.bulk_insert` and `db_utils.bulk_update` for efficient bulk operations, writes CSVs to `csv_output/`, and commits in a single transaction.
- `db_utils.py`: helper functions to centralize execute_values usage and CSV writing.

Notes & troubleshooting

- Missing environment variables: the script will fail when attempting to connect to Postgres. Use a `.env` file or export variables before running.
- If you see unique/constraint violations on reruns, either TRUNCATE the tables and restart the generator, or recreate the Postgres docker volume to start with a fresh DB.
  - Example truncate: `psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}" -c "TRUNCATE order_items, orders, products, customers RESTART IDENTITY CASCADE;"`
- If you want a migrations workflow (recommended if the schema will change over time), switch to Alembic: scaffold `alembic/`, point `target_metadata` to `models.Base.metadata`, autogenerate an initial revision, and then use `alembic upgrade head`.

Optional: persistent file logging (example)

If you want logs written to disk as well as console, add a rotating file handler. Example snippet (drop into `data_generator.py` near the top where logging is configured):

```python
from logging.handlers import RotatingFileHandler
from pathlib import Path
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)
handler = RotatingFileHandler(log_dir / 'data_generator.log', maxBytes=10_000_000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
```

License

This repository contains example code for assessment/demo use. Use as you wish.
