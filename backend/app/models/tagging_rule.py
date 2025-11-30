"""Tagging rule models for auto-tagging."""
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class TaggingRule(Base):
    """User-defined auto-tagging rules."""

    __tablename__ = "tagging_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Flexible conditions (JSON)
    conditions = Column(JSONB, nullable=False)

    # Tags to apply (array of UUIDs)
    tag_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)

    # Rule metadata
    priority = Column(Integer, default=0)
    confidence = Column(Numeric(3, 2), default=0.90)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    applications = relationship("TaggingRuleApplication", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TaggingRule {self.name}>"


class TaggingRuleApplication(Base):
    """Audit trail for rule applications."""

    __tablename__ = "tagging_rule_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("tagging_rules.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    rule = relationship("TaggingRule", back_populates="applications")

    def __repr__(self):
        return f"<TaggingRuleApplication {self.rule_id} -> {self.transaction_id}>"
