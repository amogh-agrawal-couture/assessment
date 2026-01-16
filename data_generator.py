import os
import random
import argparse
from pathlib import Path
from faker import Faker
import psycopg2
from dotenv import load_dotenv
from decimal import Decimal
from schemas.schemas import Customer, Product, Order, OrderItem
from db_utils import bulk_insert, bulk_update, write_csv

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

    # Generate customers and validate
    customers = []
    for _ in range(args.customers):
        cust = {
            "customer_name": fake.name(),
            "email": fake.unique.email(),
            "signup_date": fake.date_between("-2y", "today"),
        }
        Customer.model_validate(cust)
        customers.append((cust["customer_name"], cust["email"], cust["signup_date"]))

    customers_db = bulk_insert(
        cur,
        "customers",
        ["customer_name", "email", "signup_date"],
        customers,
        returning=["customer_id", "customer_name", "email", "signup_date"]
    )

    customer_ids = [c[0] for c in customers_db]

    write_csv(
        OUTPUT_DIR / "customers.csv",
        ["customer_id", "customer_name", "email", "signup_date"],
        customers_db,
    )

    # Generate products
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]
    products = []
    for _ in range(args.products):
        prod = {"product_name": fake.word().capitalize(), "category": random.choice(categories)}
        Product.model_validate(prod)
        products.append((prod["product_name"], prod["category"]))

    products_db = bulk_insert(
        cur,
        "products",
        ["product_name", "category"],
        products,
        returning=["product_id", "product_name", "category"]
    )

    product_ids = [p[0] for p in products_db]

    write_csv(
        OUTPUT_DIR / "products.csv",
        ["product_id", "product_name", "category"],
        products_db,
    )

    # Generate orders
    orders = []
    for _ in range(args.orders):
        orders.append((random.choice(customer_ids), fake.date_between("-18m", "today"), Decimal("0.0")))

    orders_db = bulk_insert(
        cur,
        "orders",
        ["customer_id", "order_date", "total_amount"],
        orders,
        returning=["order_id", "customer_id", "order_date"]
    )

    # Generate order items
    order_items = []
    orders_csv = []

    for order_id, customer_id, order_date in orders_db:
        total = Decimal("0.0")
        for _ in range(random.randint(1, 6)):
            qty = random.randint(1, 5)
            price_f = round(random.uniform(5, 500), 2)
            price = Decimal(f"{price_f:.2f}")
            product_id = random.choice(product_ids)
            total += price * qty
            OrderItem.model_validate({
                "order_id": order_id,
                "product_id": product_id,
                "quantity": qty,
                "price_per_unit": price,
            })
            order_items.append((order_id, product_id, qty, price))

        Order.model_validate({"customer_id": customer_id, "order_date": order_date, "total_amount": total})
        orders_csv.append((order_id, customer_id, order_date, total))

    bulk_insert(
        cur,
        "order_items",
        ["order_id", "product_id", "quantity", "price_per_unit"],
        order_items
    )

    bulk_update(
        cur,
        "orders",
        {"total_amount": "c.col1"},
        [(o[0], o[3]) for o in orders_csv],
        "o.order_id = c.col0"
    )

    write_csv(
        OUTPUT_DIR / "orders.csv",
        ["order_id", "customer_id", "order_date", "total_amount"],
        orders_csv,
    )

    write_csv(
        OUTPUT_DIR / "order_items.csv",
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