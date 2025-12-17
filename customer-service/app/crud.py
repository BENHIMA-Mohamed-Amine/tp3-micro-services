from typing import List, Optional
from sqlmodel import Session, select
from app.models import Customer, CustomerCreate, CustomerUpdate


def get_customer(session: Session, customer_id: int) -> Optional[Customer]:
    """Get a customer by ID"""
    return session.get(Customer, customer_id)


def get_customers(session: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    """Get a list of customers with pagination"""
    statement = select(Customer).offset(skip).limit(limit)
    results = session.exec(statement)
    return results.all()


def create_customer(session: Session, customer: CustomerCreate) -> Customer:
    """Create a new customer"""
    db_customer = Customer.model_validate(customer)
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)
    return db_customer


def update_customer(
    session: Session, customer_id: int, customer_data: CustomerUpdate
) -> Optional[Customer]:
    """Update an existing customer"""
    db_customer = session.get(Customer, customer_id)
    if not db_customer:
        return None
    
    # Update only provided fields
    customer_dict = customer_data.model_dump(exclude_unset=True)
    for key, value in customer_dict.items():
        setattr(db_customer, key, value)
    
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)
    return db_customer


def delete_customer(session: Session, customer_id: int) -> bool:
    """Delete a customer"""
    db_customer = session.get(Customer, customer_id)
    if not db_customer:
        return False
    
    session.delete(db_customer)
    session.commit()
    return True