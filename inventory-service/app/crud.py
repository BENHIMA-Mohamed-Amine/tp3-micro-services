from sqlmodel import Session, select
from .models import Product, ProductCreate, ProductUpdate


def get_product(session: Session, product_id: int):
    return session.get(Product, product_id)


def get_products(session: Session, skip: int = 0, limit: int = 100):
    return session.exec(select(Product).offset(skip).limit(limit)).all()


def create_product(session: Session, product: ProductCreate):
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


def update_stock(session: Session, product_id: int, quantity_delta: int):
    product = get_product(session, product_id)
    if not product:
        return None
    product.quantity += quantity_delta
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

def update_product(session: Session, product_id: int, product_data: ProductUpdate):
    db_product = session.get(Product, product_id)
    if not db_product:
        return None

    # Update only the fields that were provided (exclude_unset=True)
    hero_data = product_data.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product