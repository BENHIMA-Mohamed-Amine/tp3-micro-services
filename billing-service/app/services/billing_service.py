from decimal import Decimal
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models import Bill, BillItem, BillCreate

# We import the global client instances we created
from app.clients.customer_client import customer_client
from app.clients.products_client import products_client


class BillingService:
    def __init__(self, session: Session):
        self.session = session

    async def create_bill(self, bill_data: BillCreate) -> Bill:
        """
        Create a new bill. This involves:
        1. Verifying customer exists.
        2. Verifying products exist and getting current prices.
        3. Decrementing stock for each product.
        4. Calculating totals and saving to DB.
        """

        # --- Step 1: Validate Customer ---
        customer = await customer_client.get_customer(bill_data.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {bill_data.customer_id} not found",
            )

        # --- Step 2: Process Items & Calculate Totals ---
        bill_items: List[BillItem] = []
        total_amount = Decimal("0.00")

        for item_data in bill_data.items:
            # A. Get Product Details (to get the real price)
            product = await products_client.get_product(item_data.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item_data.product_id} not found",
                )

            # B. Check if sufficient stock is available (Optional, usually handled by inventory service error)
            # But we will rely on the decrease_stock call to fail if stock is low.

            # C. Decrease Stock in Inventory Service
            # This is a critical side effect. If this fails (e.g. insufficient stock),
            # the whole bill creation should fail.
            try:
                await products_client.decrease_stock(
                    item_data.product_id, item_data.quantity
                )
            except Exception as e:
                # If stock update fails, we stop everything.
                # Note: In a real production app, you might need a "Saga" pattern to rollback
                # previous items if the 3rd item fails. For this workshop, we abort.
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to update stock for product {item_data.product_id}: {str(e)}",
                )

            # D. Prepare Bill Item
            # We trust the price from the Inventory Service, not the user input
            price = Decimal(str(product["price"]))
            quantity = item_data.quantity
            sub_total = price * quantity

            bill_item = BillItem(
                product_id=item_data.product_id,
                quantity=quantity,
                price=price,
                sub_total=sub_total,
            )

            bill_items.append(bill_item)
            total_amount += sub_total

        # --- Step 3: Save to Database ---
        # Create the Bill object
        bill = Bill(
            customer_id=bill_data.customer_id,
            total_amount=total_amount,
            items=bill_items,  # SQLModel will handle the relationship automatically
        )

        self.session.add(bill)
        self.session.commit()
        self.session.refresh(bill)

        return bill

    def get_bill(self, bill_id: int) -> Optional[Bill]:
        """Get a bill by ID"""
        return self.session.get(Bill, bill_id)

    def list_bills(self, skip: int = 0, limit: int = 100) -> List[Bill]:
        """List all bills with pagination"""
        statement = select(Bill).offset(skip).limit(limit)
        return self.session.exec(statement).all()
