"""Tag schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TagBase(BaseModel):
    """Base tag schema."""
    display_name: str
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None


class TagCreate(TagBase):
    """Schema for creating tags."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating tags."""
    display_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Tag(TagBase):
    """Schema for tag responses."""
    id: UUID
    user_id: UUID
    name: str
    usage_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagList(BaseModel):
    """Schema for tag list."""
    tags: List[Tag]
    total: int
