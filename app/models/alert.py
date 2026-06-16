from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AlertSeverity(str, enum.Enum):
    low = "low"
    critical = "critical"
    out_of_stock = "out_of_stock"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    product = relationship("Product", back_populates="alerts")
