from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from ..database import get_session
from .. import crud, models

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=models.ProductRead)
def create_product(
    product: models.ProductCreate, session: Session = Depends(get_session)
):
    return crud.create_product(session, product)


@router.get("/", response_model=List[models.ProductRead])
def read_products(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return crud.get_products(session, skip, limit)


@router.get("/{product_id}", response_model=models.ProductRead)
def read_product(product_id: int, session: Session = Depends(get_session)):
    product = crud.get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}/stock", response_model=models.ProductRead)
def adjust_stock(
    product_id: int, quantity_delta: int, session: Session = Depends(get_session)
):
    product = crud.update_stock(session, product_id, quantity_delta)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
