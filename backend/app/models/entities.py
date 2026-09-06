"""
SQLAlchemy ORM Database Models
==============================
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="inventory_planner")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scenarios = relationship("Scenario", back_populates="user")


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String(50), primary_key=True, index=True)
    store_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    region = Column(String(100), default="North America")
    created_at = Column(DateTime, default=datetime.utcnow)

    sales = relationship("Sale", back_populates="store")
    inventory_items = relationship("Inventory", back_populates="store")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), index=True, nullable=False)
    subcategory = Column(String(100), default="General")
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    lead_time_days = Column(Integer, default=5)
    min_order_qty = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    sales = relationship("Sale", back_populates="product")
    inventory_items = relationship("Inventory", back_populates="product")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_date = Column(Date, index=True, nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    units_sold = Column(Integer, default=0, nullable=False)
    revenue = Column(Float, default=0.0)
    discount_rate = Column(Float, default=0.0)
    is_promotion = Column(Boolean, default=False)
    is_holiday = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="sales")
    product = relationship("Product", back_populates="sales")

    __table_args__ = (
        Index("idx_sales_store_prod_date", "store_id", "product_id", "sale_date", unique=True),
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), ForeignKey("stores.store_id"), index=True, nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True, nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    safety_stock = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    max_capacity = Column(Integer, default=1000)
    last_restock_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")

    __table_args__ = (
        Index("idx_inv_store_prod", "store_id", "product_id", unique=True),
    )


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    store_id = Column(String(50), ForeignKey("stores.store_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    input_parameters = Column(JSON, nullable=False)
    simulation_results = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scenarios")
