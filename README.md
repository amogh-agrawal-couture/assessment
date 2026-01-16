# Assessment Data Generator

Small utility to generate sample e‑commerce data (customers, products, orders, order items) into a PostgreSQL database and write CSV exports to `csv_output/`.

This repository contains:

- `data_generator.py` — main script that creates fake customers, products, orders and order items and writes CSVs.
- `init.sql` — schema file to create the required tables and indexes.
- `requirements.txt` — Python dependencies.
- `run.sh` — convenience wrapper to run the generator (if present).
- `docker-compose.yml` — optional local Postgres service for quick testing.
- `csv_output/` — output CSV files produced by the script.

Quick plan / checklist

1. Install dependencies
2. Provide Postgres credentials via environment variables (or run Postgres via `docker-compose`)
3. Initialize DB schema (`init.sql`)
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

Environment variables

The script reads Postgres connection settings from environment variables. Create a `.env` file or export them in your shell:

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

If you have `psql` available and your database is created, run:

```bash
psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}" -f init.sql
```

Optional: start a local Postgres via Docker Compose

If you prefer, use the included `docker-compose.yml` to spin up a local Postgres instance. After `docker-compose up -d` you can run the `psql` command above using the credentials defined in the compose file.

Run the generator

Make sure the environment variables are set and then run:

```bash
python data_generator.py
```

Or use the wrapper (if present):

```bash
./run.sh
```

What the script does

- Generates fake customers (default 300), products (default 100), and orders (default 2000).
- Uses bulk inserts (`psycopg2.extras.execute_values`) and chunking to avoid per-row INSERT statements. This greatly improves performance for large datasets.
- Implements bulk inserts by calling `execute_values` directly in `data_generator.py`, and uses a small `write_csv(path, header, rows)` helper to write rows to CSV.
- Writes generated data to CSV files in `csv_output/`:
  - `customers.csv`
  - `products.csv`
  - `orders.csv`
  - `order_items.csv`

Configuration knobs

Open `data_generator.py` and change these constants near the top of the file:

- `NUM_CUSTOMERS` — number of customers to generate (default 300)
- `NUM_PRODUCTS` — number of products to generate (default 100)
- `NUM_ORDERS` — number of orders to generate (default 2000)
- `chunk_size` — passed to the bulk functions; default 500

Notes & troubleshooting

- Missing environment variables: the script will fail when attempting to connect to Postgres. Use a `.env` file or export variables before running.
- If `psycopg2` fails to install on macOS, try `pip install psycopg2-binary` (already in `requirements.txt`). If you need the non-binary build, ensure `libpq` and PostgreSQL development headers are installed via Homebrew.
- If you see unique/constraint violations on reruns, either truncate the tables or drop and recreate the DB using `init.sql`.

License

This repository contains example code for assessment/demo use. Use as you wish.

