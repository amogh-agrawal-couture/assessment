import os
import random
from faker import Faker
import psycopg2
from dotenv import load_dotenv

load_dotenv()

fake = Faker()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB"),
)

cur = conn.cursor()

# Customers
NUM_CUSTOMERS = 300
for _ in range(NUM_CUSTOMERS):
    cur.execute("""
        INSERT INTO customers (customer_name, email, signup_date)
        VALUES (%s,%s,%s)
    """, (
        fake.name(),
        fake.unique.email(),
        fake.date_between(start_date="-2y", end_date="today")
    ))

# Products
categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]
for _ in range(100):
    cur.execute("""
        INSERT INTO products (product_name, category)
        VALUES (%s,%s)
    """, (
        fake.word().capitalize(),
        random.choice(categories)
    ))

# Orders
for _ in range(2000):
    cur.execute("""
        INSERT INTO orders (customer_id, order_date, total_amount)
        VALUES (%s,%s,0) RETURNING order_id
    """, (
        random.randint(1, NUM_CUSTOMERS),
        fake.date_between(start_date="-18m", end_date="today")
    ))

    order_id = cur.fetchone()[0]
    total = 0

    for _ in range(random.randint(1, 6)):
        price = round(random.uniform(5, 500), 2)
        qty = random.randint(1, 5)
        total += price * qty

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price_per_unit)
            VALUES (%s,%s,%s,%s)
        """, (
            order_id,
            random.randint(1, 100),
            qty,
            price
        ))

    cur.execute("UPDATE orders SET total_amount=%s WHERE order_id=%s", (total, order_id))

conn.commit()
cur.close()
conn.close()

print("Data generated.")
