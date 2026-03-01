from pydantic import BaseModel
from typing import List


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float


class OrderResponse(BaseModel):
    id: int
    status: str
    total_price: float
    items: List[OrderItemResponse]
