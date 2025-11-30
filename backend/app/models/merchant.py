"""Merchant models for normalization."""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Merchant(Base):
    """Normalized merchant database."""

    __tablename__ = "merchants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    normalized_name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    category = Column(String(100))
    logo_url = Column(String(500))
    website = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patterns = relationship("MerchantPattern", back_populates="merchant", cascade="all, delete-orphan")
    default_tags = relationship("MerchantDefaultTag", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant")

    def __repr__(self):
        return f"<Merchant {self.display_name}>"


class MerchantPattern(Base):
    """Patterns for matching raw transaction titles to merchants."""

    __tablename__ = "merchant_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    pattern = Column(String(500), nullable=False)
    pattern_type = Column(String(50), default="substring")  # substring, regex, exact
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="patterns")

    def __repr__(self):
        return f"<MerchantPattern {self.pattern} ({self.pattern_type})>"


class MerchantDefaultTag(Base):
    """Default tags for merchants (auto-tagging)."""

    __tablename__ = "merchant_default_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    confidence = Column(Numeric(3, 2), default=0.85)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="default_tags")

    __table_args__ = (
        UniqueConstraint('merchant_id', 'tag_name', name='uq_merchant_tag'),
    )

    def __repr__(self):
        return f"<MerchantDefaultTag {self.tag_name}>"
