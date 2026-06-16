from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.alert import AlertSeverity


class AlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    current_stock: int
    min_threshold: int
    shortage: int
    severity: AlertSeverity
    is_active: bool
    triggered_at: datetime
    resolved_at: Optional[datetime]

    model_config = {"from_attributes": True}