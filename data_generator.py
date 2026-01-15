import os
import random
import csv
import argparse
from pathlib import Path
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

parser = argparse.ArgumentParser(description="Generate fake e-commerce data")
parser.add_argument("--customers", type=int, default=300)
parser.add_argument("--products", type=int, default=100)
parser.add_argument("--orders", type=int, default=2000)
args = parser.parse_args()

load_dotenv()
fake = Faker()

OUTPUT_DIR = Path("csv_output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = None
cur = None

try:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )
    cur = conn.cursor()

    customers = [
        (fake.name(), fake.unique.email(), fake.date_between("-2y", "today"))
        for _ in range(args.customers)
    ]

    execute_values(
        cur,
        """
        INSERT INTO customers (customer_name, email, signup_date)
        VALUES %s
        RETURNING customer_id, customer_name, email, signup_date
        """,
        customers,
    )

    customers_db = cur.fetchall()
    customer_ids = [c[0] for c in customers_db]

    def write_csv(filename, headers, rows):
        with open(OUTPUT_DIR / filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    write_csv(
        "customers.csv",
        ["customer_id", "customer_name", "email", "signup_date"],
        customers_db,
    )

    categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]

    products = [
        (fake.word().capitalize(), random.choice(categories))
        for _ in range(args.products)
    ]

    execute_values(
        cur,
        """
        INSERT INTO products (product_name, category)
        VALUES %s
        RETURNING product_id, product_name, category
        """,
        products,
    )

    products_db = cur.fetchall()
    product_ids = [p[0] for p in products_db]

    write_csv(
        "products.csv",
        ["product_id", "product_name", "category"],
        products_db,
    )

    orders = [
        (
            random.choice(customer_ids),
            fake.date_between("-18m", "today"),
            0.0,
        )
        for _ in range(args.orders)
    ]

    execute_values(
        cur,
        """
        INSERT INTO orders (customer_id, order_date, total_amount)
        VALUES %s
        RETURNING order_id, customer_id, order_date
        """,
        orders,
    )

    orders_db = cur.fetchall()
    order_items = []
    orders_csv = []

    for order_id, customer_id, order_date in orders_db:
        total = 0
        for _ in range(random.randint(1, 6)):
            qty = random.randint(1, 5)
            price = round(random.uniform(5, 500), 2)
            product_id = random.choice(product_ids)
            total += qty * price
            order_items.append((order_id, product_id, qty, price))

        orders_csv.append((order_id, customer_id, order_date, total))

    execute_values(
        cur,
        """
        INSERT INTO order_items (order_id, product_id, quantity, price_per_unit)
        VALUES %s
        """,
        order_items,
    )

    execute_values(
        cur,
        """
        UPDATE orders AS o
        SET total_amount = c.total
        FROM (VALUES %s) AS c(order_id, total)
        WHERE o.order_id = c.order_id
        """,
        [(o[0], o[3]) for o in orders_csv],
    )

    write_csv(
        "orders.csv",
        ["order_id", "customer_id", "order_date", "total_amount"],
        orders_csv,
    )

    write_csv(
        "order_items.csv",
        ["order_id", "product_id", "quantity", "price_per_unit"],
        order_items,
    )

    conn.commit()

except Exception:
    if conn:
        conn.rollback()
    raise

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()

print("Data generated")
