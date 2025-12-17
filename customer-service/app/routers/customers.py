from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.models import CustomerCreate, CustomerRead, CustomerUpdate
from app import crud

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=List[CustomerRead])
def list_customers(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """Get a list of all customers with pagination"""
    customers = crud.get_customers(session, skip=skip, limit=limit)
    return customers


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, session: Session = Depends(get_session)):
    """Get a specific customer by ID"""
    customer = crud.get_customer(session, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found",
        )
    return customer


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, session: Session = Depends(get_session)):
    """Create a new customer"""
    try:
        db_customer = crud.create_customer(session, customer)
        return db_customer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating customer: {str(e)}",
        )


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    session: Session = Depends(get_session),
):
    """Update an existing customer"""
    updated_customer = crud.update_customer(session, customer_id, customer_data)
    if not updated_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found",
        )
    return updated_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, session: Session = Depends(get_session)):
    """Delete a customer"""
    success = crud.delete_customer(session, customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found",
        )
    return None
