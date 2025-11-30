"""Transaction API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from uuid import UUID

from app.database import get_db
from app.schemas.transaction import Transaction, TransactionList, TransactionUpdate
from app.models import Transaction as TransactionModel, TransactionTag, Tag, User

router = APIRouter()


def get_default_user(db: Session) -> User:
    """Get default user for MVP."""
    user = db.query(User).filter(User.email == 'default@finance.local').first()
    if not user:
        raise HTTPException(status_code=500, detail="Default user not found")
    return user


@router.get("/transactions", response_model=TransactionList)
async def list_transactions(
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List transactions with pagination and filters.

    Args:
        from_date: Filter by booking date >= from_date
        to_date: Filter by booking date <= to_date
        limit: Number of results (max 500)
        offset: Offset for pagination
        db: Database session

    Returns:
        Paginated list of transactions
    """
    user = get_default_user(db)

    # Build query with eager loading of tags
    query = db.query(TransactionModel).options(
        joinedload(TransactionModel.tags)
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False
    )

    # Apply date filters
    if from_date:
        query = query.filter(TransactionModel.booking_date >= from_date)
    if to_date:
        query = query.filter(TransactionModel.booking_date <= to_date)

    # Get total count
    total = query.count()

    # Get paginated results
    transactions = query.order_by(
        TransactionModel.booking_date.desc()
    ).offset(offset).limit(limit).all()

    # Calculate page number
    page = (offset // limit) + 1 if limit > 0 else 1

    return TransactionList(
        transactions=transactions,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Get single transaction by ID.

    Args:
        transaction_id: Transaction UUID
        db: Database session

    Returns:
        Transaction details
    """
    try:
        txn_uuid = UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    transaction = db.query(TransactionModel).filter(
        TransactionModel.id == txn_uuid
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.patch("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update transaction.

    Args:
        transaction_id: Transaction UUID
        update_data: Update payload
        db: Database session

    Returns:
        Updated transaction
    """
    try:
        txn_uuid = UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    transaction = db.query(TransactionModel).filter(
        TransactionModel.id == txn_uuid
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete transaction (hide).

    Args:
        transaction_id: Transaction UUID
        db: Database session

    Returns:
        Success message
    """
    try:
        txn_uuid = UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    transaction = db.query(TransactionModel).filter(
        TransactionModel.id == txn_uuid
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Soft delete
    transaction.is_hidden = True
    db.commit()

    return {"message": "Transaction hidden successfully"}
