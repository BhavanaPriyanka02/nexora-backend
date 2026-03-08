from pydantic import BaseModel, EmailStr
from typing import Optional


class ProductBase(BaseModel):
    name: str
    price: float
    stock: int
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

