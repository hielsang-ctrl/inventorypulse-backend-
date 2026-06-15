from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class MovementType(str, enum.Enum):
    in_ = "in"
    out = "out"


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=True)
    reason = Column(String(500), nullable=True)
    movement_date = Column(Date, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="stock_movements")
    supplier = relationship("Supplier", backref="stock_movements")
    user = relationship("User", backref="stock_movements")
