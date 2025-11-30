"""Tag models for flat tagging system."""
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Tag(Base):
    """Flat tag system - no hierarchies."""

    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)  # Normalized: "food"
    display_name = Column(String(100), nullable=False)  # Display: "Food"
    color = Column(String(7))  # Hex color
    icon = Column(String(50))
    description = Column(Text)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    transaction_tags = relationship("TransactionTag", back_populates="tag", cascade="all, delete-orphan")
    synonyms = relationship("TagSynonym", back_populates="canonical_tag", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )

    def __repr__(self):
        return f"<Tag {self.display_name}>"


class TagSynonym(Base):
    """Tag synonyms for NLP-based duplicate detection."""

    __tablename__ = "tag_synonyms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    canonical_tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    synonym = Column(String(100), nullable=False)
    source = Column(String(50), default="manual")  # manual, nlp_suggested, auto_merged
    confidence = Column(Numeric(3, 2))  # NLP similarity score
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    canonical_tag = relationship("Tag", back_populates="synonyms")

    __table_args__ = (
        UniqueConstraint('user_id', 'synonym', name='uq_user_synonym'),
    )

    def __repr__(self):
        return f"<TagSynonym {self.synonym} -> {self.canonical_tag_id}>"


class TransactionTag(Base):
    """Many-to-many relationship between transactions and tags."""

    __tablename__ = "transaction_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), default="manual")  # manual, auto_rule, auto_merchant, auto_nlp
    confidence = Column(Numeric(3, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="transaction_tags")
    tag = relationship("Tag", back_populates="transaction_tags")

    __table_args__ = (
        UniqueConstraint('transaction_id', 'tag_id', name='uq_transaction_tag'),
    )

    def __repr__(self):
        return f"<TransactionTag {self.transaction_id} - {self.tag_id}>"
