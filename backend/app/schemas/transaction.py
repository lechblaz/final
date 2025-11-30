"""Transaction schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from app.schemas.tag import Tag


class TransactionBase(BaseModel):
    """Base transaction schema."""
    booking_date: date
    transaction_date: date
    operation_type: str
    title: str
    sender_recipient: Optional[str] = None
    account_number: Optional[str] = None
    amount: Decimal
    balance_after: Optional[Decimal] = None
    currency: str = "PLN"
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema for creating transactions."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating transactions."""
    notes: Optional[str] = None
    is_hidden: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class Transaction(TransactionBase):
    """Schema for transaction responses."""
    id: UUID
    user_id: UUID
    transaction_hash: str
    # Merchant enrichment (Phase 2)
    normalized_merchant_name: Optional[str] = None
    store_identifier: Optional[str] = None
    location_extracted: Optional[str] = None
    raw_merchant_text: Optional[str] = None
    merchant_confidence: Optional[Decimal] = None
    # Tags (Phase 3)
    tags: List[Tag] = []
    is_hidden: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionList(BaseModel):
    """Schema for paginated transaction list."""
    transactions: List[Transaction]
    total: int
    page: int
    page_size: int
