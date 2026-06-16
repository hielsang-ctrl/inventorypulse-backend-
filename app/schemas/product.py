from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    ...

class ProductUpdate(BaseModel):
    ...

class ProductResponse(BaseModel):
    ...