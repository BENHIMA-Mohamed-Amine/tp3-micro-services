from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class CustomerBase(SQLModel):
    """Base customer model with shared fields"""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(unique=True, index=True)


class Customer(CustomerBase, table=True):
    """Customer database model"""
    id: Optional[int] = Field(default=None, primary_key=True)


class CustomerCreate(CustomerBase):
    """Schema for creating a customer (no id)"""
    pass


class CustomerRead(CustomerBase):
    """Schema for reading a customer (with id)"""
    id: int


class CustomerUpdate(SQLModel):
    """Schema for updating a customer (all fields optional)"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None