from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    unit_of_measure = Column(String(50), default="unit")
    unit_cost = Column(Numeric(12, 2), default=0)
    selling_price = Column(Numeric(12, 2), default=0)
    current_stock = Column(Integer, default=0)
    min_threshold = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", backref="products")
    stock_movements = relationship("StockMovement", back_populates="product")
    alerts = relationship("Alert", back_populates="product")
