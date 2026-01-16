from pydantic import BaseModel, EmailStr, validator
from datetime import date
from decimal import Decimal


class Customer(BaseModel):
    customer_name: str
    email: EmailStr
    signup_date: date


class Product(BaseModel):
    product_name: str
    category: str


class Order(BaseModel):
    customer_id: int
    order_date: date
    total_amount: Decimal


class OrderItem(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price_per_unit: Decimal

    @validator("quantity")
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity must be > 0")
        return v
