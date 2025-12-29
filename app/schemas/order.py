import datetime
from pydantic import BaseModel, ConfigDict
from typing import List


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float  # Важное поле!

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    created_at: datetime.datetime
    status: str
    total_price: float
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)