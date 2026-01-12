import os
import random
import csv
from pathlib import Path
from faker import Faker
import psycopg2
from dotenv import load_dotenv

load_dotenv()
fake = Faker()

OUTPUT_DIR = Path("csv_output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB"),
)
cur = conn.cursor()

# ---------------- Customers ----------------
NUM_CUSTOMERS = 300
customers_csv = []

for _ in range(NUM_CUSTOMERS):
    name = fake.name()
    email = fake.unique.email()
    signup = fake.date_between(start_date="-2y", end_date="today")

    customers_csv.append((name, email, signup))

    cur.execute("""
        INSERT INTO customers (customer_name, email, signup_date)
        VALUES (%s,%s,%s)
    """, (name, email, signup))

# Write customers CSV
with open(OUTPUT_DIR / "customers.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["customer_name", "email", "signup_date"])
    writer.writerows(customers_csv)

# ---------------- Products ----------------
categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]
products_csv = []

for _ in range(100):
    product_name = fake.word().capitalize()
    category = random.choice(categories)

    products_csv.append((product_name, category))

    cur.execute("""
        INSERT INTO products (product_name, category)
        VALUES (%s,%s)
    """, (product_name, category))

with open(OUTPUT_DIR / "products.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["product_name", "category"])
    writer.writerows(products_csv)

# ---------------- Orders & Order Items ----------------
orders_csv = []
order_items_csv = []

for _ in range(2000):
    customer_id = random.randint(1, NUM_CUSTOMERS)
    order_date = fake.date_between(start_date="-18m", end_date="today")

    cur.execute("""
        INSERT INTO orders (customer_id, order_date, total_amount)
        VALUES (%s,%s,0) RETURNING order_id
    """, (customer_id, order_date))

    order_id = cur.fetchone()[0]
    total = 0

    for _ in range(random.randint(1, 6)):
        product_id = random.randint(1, 100)
        qty = random.randint(1, 5)
        price = round(random.uniform(5, 500), 2)
        total += qty * price

        order_items_csv.append((order_id, product_id, qty, price))

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price_per_unit)
            VALUES (%s,%s,%s,%s)
        """, (order_id, product_id, qty, price))

    orders_csv.append((order_id, customer_id, order_date, total))
    cur.execute("UPDATE orders SET total_amount=%s WHERE order_id=%s", (total, order_id))

# Write orders CSV
with open(OUTPUT_DIR / "orders.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "order_date", "total_amount"])
    writer.writerows(orders_csv)

# Write order items CSV
with open(OUTPUT_DIR / "order_items.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "product_id", "quantity", "price_per_unit"])
    writer.writerows(order_items_csv)

conn.commit()
cur.close()
conn.close()

print("Data generated + CSV files created.")
