from pydantic import BaseModel
from typing import Optional


# 🔹 Base Schema
class ProductBase(BaseModel):
    name: str
    price: float
    stock: int
    image_url: str
    category: str


# 🔹 Create Product
class ProductCreate(ProductBase):
    pass


# 🔹 Update Product (Optional fields)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


# 🔹 Response Schema
class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
