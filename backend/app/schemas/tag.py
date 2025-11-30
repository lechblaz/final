"""Tag schemas."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TagBase(BaseModel):
    """Base tag schema."""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class TagCreate(BaseModel):
    """Schema for creating tags."""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class TagUpdate(BaseModel):
    """Schema for updating tags."""
    display_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Tag(BaseModel):
    """Schema for tag responses."""
    id: UUID
    name: str
    display_name: str
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    usage_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagWithStats(Tag):
    """Tag with transaction statistics."""
    transaction_count: int = 0


class TagListResponse(BaseModel):
    """Response for tag list."""
    tags: List[TagWithStats]
    total: int


# ============================================
# Transaction Tagging Schemas
# ============================================

class TransactionTagCreate(BaseModel):
    """Schema for creating a transaction-tag association."""
    transaction_id: UUID
    tag_id: UUID
    source: str = 'manual'
    confidence: Optional[float] = 1.0


class TransactionTagsUpdate(BaseModel):
    """Schema for updating tags on a transaction."""
    tag_ids: List[UUID] = Field(default_factory=list)


class TransactionTag(BaseModel):
    """Full transaction-tag schema."""
    id: UUID
    transaction_id: UUID
    tag_id: UUID
    source: str
    confidence: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
