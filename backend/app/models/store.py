"""Store model for specific merchant locations."""
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Store(Base):
    """Store model for specific merchant locations with addresses."""

    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    store_identifier = Column(String(100), nullable=False)
    store_name = Column(String(255))
    address = Column(Text)
    city = Column(String(255), index=True)
    postal_code = Column(String(20))
    country = Column(String(100), default="Poland")
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="stores")
    transactions = relationship("Transaction", back_populates="store")

    def __repr__(self):
        return f"<Store {self.merchant.display_name if self.merchant else 'Unknown'} - {self.store_identifier}>"
