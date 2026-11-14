from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal 

class OrderCreate(BaseModel):
    supplier_id: int = Field(gt=0)

class OrderItemCreate(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    supplier_id: int
    status: str
    total_price: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

    