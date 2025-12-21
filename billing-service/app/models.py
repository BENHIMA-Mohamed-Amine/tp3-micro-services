from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


# --- Bill Item Models ---
class BillItemBase(SQLModel):
    product_id: int
    quantity: int
    price: Decimal = Field(default=0.0, decimal_places=2)


class BillItem(BillItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bill_id: Optional[int] = Field(default=None, foreign_key="bill.id")
    sub_total: Decimal = Field(decimal_places=2)

    bill: Optional["Bill"] = Relationship(back_populates="items")


# --- Bill Models ---
class BillBase(SQLModel):
    customer_id: int
    bill_date: datetime = Field(default_factory=datetime.now)


class Bill(BillBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    total_amount: Decimal = Field(default=0.0, decimal_places=2)

    items: List["BillItem"] = Relationship(back_populates="bill")


# --- DTOs (Data Transfer Objects) ---
class BillItemCreate(SQLModel):
    product_id: int
    quantity: int


class BillCreate(SQLModel):
    customer_id: int
    items: List[BillItemCreate]


class BillRead(BillBase):
    id: int
    total_amount: Decimal
    items: List[BillItem]
