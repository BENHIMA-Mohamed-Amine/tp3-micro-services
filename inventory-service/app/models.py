from typing import Optional
from sqlmodel import SQLModel, Field


class ProductBase(SQLModel):
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
