"""Pydantic schemas for merchants and stores."""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ============================================
# Merchant Schemas
# ============================================

class MerchantBase(BaseModel):
    """Base merchant schema."""
    normalized_name: str
    display_name: str
    category: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None


class MerchantCreate(MerchantBase):
    """Schema for creating a merchant."""
    pass


class MerchantUpdate(BaseModel):
    """Schema for updating a merchant."""
    display_name: Optional[str] = None
    category: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None


class Merchant(MerchantBase):
    """Full merchant schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MerchantWithStats(MerchantBase):
    """Merchant with transaction statistics."""
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    transaction_count: int = 0
    store_count: int = 0
    total_spent: float = 0.0


# ============================================
# Store Schemas
# ============================================

class StoreBase(BaseModel):
    """Base store schema."""
    merchant_id: UUID
    store_identifier: str
    store_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Poland"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class StoreCreate(StoreBase):
    """Schema for creating a store."""
    pass


class StoreUpdate(BaseModel):
    """Schema for updating a store."""
    store_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class Store(StoreBase):
    """Full store schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoreWithMerchant(Store):
    """Store with merchant info."""
    merchant: Merchant


class StoreWithStats(Store):
    """Store with transaction statistics."""
    merchant: Merchant
    transaction_count: int = 0
    total_spent: float = 0.0


# ============================================
# List Responses
# ============================================

class MerchantListResponse(BaseModel):
    """Response for merchant list."""
    merchants: list[MerchantWithStats]
    total: int


class StoreListResponse(BaseModel):
    """Response for store list."""
    stores: list[StoreWithStats]
    total: int
