from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.models.stock_movement import MovementType


class StockInCreate(BaseModel):
    ...

class StockOutCreate(BaseModel):
    ...

class StockMovementResponse(BaseModel):
    ...