from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import BillRead, BillCreate
from app.services.billing_service import BillingService

router = APIRouter(prefix="/bills", tags=["bills"])

@router.get("", response_model=List[BillRead])
def list_bills(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """List bills with pagination"""
    service = BillingService(session)
    return service.list_bills(skip=skip, limit=limit)

@router.post("", response_model=BillRead, status_code=status.HTTP_201_CREATED)
async def create_bill(bill_data: BillCreate, session: Session = Depends(get_session)):
    service = BillingService(session)
    return await service.create_bill(bill_data)


@router.get("/{bill_id}", response_model=BillRead)
def get_bill(bill_id: int, session: Session = Depends(get_session)):
    service = BillingService(session)
    bill = service.get_bill(bill_id)

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bill with id {bill_id} not found",
        )

    return bill
