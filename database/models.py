"""
數據庫模型 — 6 張表
"""
from sqlalchemy import (
    Column, Integer, Float, String, Text, DateTime, ForeignKey, Boolean, create_engine, Enum
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()


class Station(Base):
    """監測站"""
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    river_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    device_id = Column(String(50), nullable=True)
    status = Column(String(20), default="online")  # online/offline/maintenance
    description = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sensor_data = relationship("SensorData", back_populates="station", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="station", cascade="all, delete-orphan")


class SensorData(Base):
    """傳感器數據"""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    temperature = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    turbidity = Column(Float, nullable=True)
    dissolved_oxygen = Column(Float, nullable=True)
    conductivity = Column(Float, nullable=True)
    ammonia_nitrogen = Column(Float, nullable=True)
    total_phosphorus = Column(Float, nullable=True)
    battery = Column(Float, nullable=True)
    signal_strength = Column(Float, nullable=True)
    recorded_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    station = relationship("Station", back_populates="sensor_data")


class Alert(Base):
    """警報"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    alert_type = Column(String(30), nullable=False)
    severity = Column(String(10), default="warning")  # info/warning/critical
    message = Column(Text, nullable=False)
    sensor_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    station = relationship("Station", back_populates="alerts")


class Product(Base):
    """商城商品"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    image_url = Column(String(300), default="")
    stock = Column(Integer, default=0)
    category = Column(String(50), default="other")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    orders = relationship("Order", back_populates="product")


class Order(Base):
    """訂單"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending/confirmed/shipped
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="orders")


class Feedback(Base):
    """用戶反饋"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(100), nullable=False)
    email = Column(String(200), default="")
    category = Column(String(50), default="general")
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
