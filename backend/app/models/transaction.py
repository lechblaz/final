"""Transaction and import batch models."""
from sqlalchemy import Column, String, Integer, Numeric, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ImportBatch(Base):
    """Import batch tracking for CSV uploads."""

    __tablename__ = "import_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    account_number = Column(String(50))
    account_type = Column(String(100))
    currency = Column(String(3), default="PLN")
    period_start = Column(Date)
    period_end = Column(Date)
    raw_content = Column(Text)
    transactions_imported = Column(Integer, default=0)
    duplicates_skipped = Column(Integer, default=0)
    import_status = Column(String(50), default="processing")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="import_batch")

    def __repr__(self):
        return f"<ImportBatch {self.file_name} - {self.import_status}>"


class Transaction(Base):
    """Transaction model for financial transactions."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    import_batch_id = Column(UUID(as_uuid=True), ForeignKey("import_batches.id", ondelete="SET NULL"))

    # Deduplication
    transaction_hash = Column(String(64), unique=True, nullable=False, index=True)

    # Core transaction data
    booking_date = Column(Date, nullable=False, index=True)
    transaction_date = Column(Date, nullable=False)
    operation_type = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    sender_recipient = Column(String(500))
    account_number = Column(String(50))
    amount = Column(Numeric(15, 2), nullable=False, index=True)
    balance_after = Column(Numeric(15, 2))
    currency = Column(String(3), default="PLN")

    # Enrichment
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="SET NULL"))
    normalized_merchant_name = Column(String(255))
    merchant_confidence = Column(Numeric(3, 2))

    # User fields
    notes = Column(Text)
    is_hidden = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    import_batch = relationship("ImportBatch", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    transaction_tags = relationship("TransactionTag", back_populates="transaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Transaction {self.booking_date} - {self.amount} {self.currency}>"
