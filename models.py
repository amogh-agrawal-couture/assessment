from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100))
    email = Column(String(100))
    signup_date = Column(Date)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    order_date = Column(Date)
    total_amount = Column(Numeric(10, 2))

    __table_args__ = (
        Index("idx_orders_date", "order_date"),
        Index("idx_orders_customer", "customer_id"),
    )


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(100))
    category = Column(String(50))

    __table_args__ = (
        Index("idx_products_category", "category"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    price_per_unit = Column(Numeric(10, 2))

    __table_args__ = (
        Index("idx_order_items_order", "order_id"),
    )

