"""Merchant API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models import Merchant, Store, Transaction, User
from app.schemas.merchant import (
    MerchantCreate,
    MerchantUpdate,
    Merchant as MerchantSchema,
    MerchantWithStats,
    MerchantListResponse,
    StoreCreate,
    StoreUpdate,
    Store as StoreSchema,
    StoreWithStats,
    StoreWithMerchant,
    StoreListResponse,
)

router = APIRouter(prefix="/merchants", tags=["merchants"])


def get_default_user(db: Session) -> User:
    """Get default user for MVP (single-user mode)."""
    user = db.query(User).filter(User.email == "default@finance.local").first()
    if not user:
        raise HTTPException(status_code=500, detail="Default user not found")
    return user


# ============================================
# Merchant Endpoints
# ============================================

@router.get("", response_model=MerchantListResponse)
def list_merchants(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all merchants with statistics.

    Returns merchants sorted by transaction count.
    """
    user = get_default_user(db)

    # Get merchants with stats from transactions
    query = db.query(
        Merchant.id,
        Merchant.normalized_name,
        Merchant.display_name,
        Merchant.category,
        Merchant.logo_url,
        Merchant.website,
        Merchant.created_at,
        Merchant.updated_at,
        func.count(Transaction.id).label('transaction_count'),
        func.count(func.distinct(Transaction.store_identifier)).label('store_count'),
        func.coalesce(func.sum(Transaction.amount), 0).label('total_spent')
    ).outerjoin(
        Transaction,
        (Transaction.normalized_merchant_name == Merchant.normalized_name) &
        (Transaction.user_id == user.id)
    ).group_by(Merchant.id)

    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Merchant.display_name.ilike(search_pattern)) |
            (Merchant.normalized_name.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    merchants = query.order_by(desc('transaction_count')).offset(offset).limit(limit).all()

    # Convert to response format
    merchant_list = [
        MerchantWithStats(
            id=m.id,
            normalized_name=m.normalized_name,
            display_name=m.display_name,
            category=m.category,
            logo_url=m.logo_url,
            website=m.website,
            created_at=m.created_at,
            updated_at=m.updated_at,
            transaction_count=m.transaction_count or 0,
            store_count=m.store_count or 0,
            total_spent=float(m.total_spent or 0)
        )
        for m in merchants
    ]

    return MerchantListResponse(merchants=merchant_list, total=total)


@router.get("/discover", response_model=MerchantListResponse)
def discover_merchants(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    min_transactions: int = Query(2, ge=1),
    db: Session = Depends(get_db),
):
    """
    Discover merchants from transactions that aren't in the merchants table yet.

    This helps identify commonly used merchants that should be added to the database.
    """
    user = get_default_user(db)

    # Find normalized_merchant_names that don't have a merchant record
    discovered = db.query(
        Transaction.normalized_merchant_name,
        func.count(Transaction.id).label('transaction_count'),
        func.count(func.distinct(Transaction.store_identifier)).label('store_count'),
        func.sum(Transaction.amount).label('total_spent')
    ).filter(
        Transaction.user_id == user.id,
        Transaction.normalized_merchant_name.isnot(None),
        ~Transaction.normalized_merchant_name.in_(
            db.query(Merchant.normalized_name)
        )
    ).group_by(
        Transaction.normalized_merchant_name
    ).having(
        func.count(Transaction.id) >= min_transactions
    ).order_by(
        desc('transaction_count')
    ).offset(offset).limit(limit).all()

    # Convert to merchant-like format
    merchant_list = [
        MerchantWithStats(
            id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder ID
            normalized_name=d.normalized_merchant_name,
            display_name=d.normalized_merchant_name,
            category=None,
            logo_url=None,
            website=None,
            created_at=None,
            updated_at=None,
            transaction_count=d.transaction_count,
            store_count=d.store_count or 0,
            total_spent=float(d.total_spent or 0)
        )
        for d in discovered
    ]

    return MerchantListResponse(merchants=merchant_list, total=len(merchant_list))


@router.post("", response_model=MerchantSchema, status_code=201)
def create_merchant(
    merchant: MerchantCreate,
    db: Session = Depends(get_db),
):
    """Create a new merchant."""
    # Check if merchant already exists
    existing = db.query(Merchant).filter(
        Merchant.normalized_name == merchant.normalized_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Merchant with normalized_name '{merchant.normalized_name}' already exists"
        )

    db_merchant = Merchant(**merchant.model_dump())
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)

    return db_merchant


@router.get("/{merchant_id}", response_model=MerchantWithStats)
def get_merchant(
    merchant_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific merchant with statistics."""
    user = get_default_user(db)

    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Get stats
    stats = db.query(
        func.count(Transaction.id).label('transaction_count'),
        func.count(func.distinct(Transaction.store_identifier)).label('store_count'),
        func.sum(Transaction.amount).label('total_spent')
    ).filter(
        Transaction.normalized_merchant_name == merchant.normalized_name,
        Transaction.user_id == user.id
    ).first()

    return MerchantWithStats(
        id=merchant.id,
        normalized_name=merchant.normalized_name,
        display_name=merchant.display_name,
        category=merchant.category,
        logo_url=merchant.logo_url,
        website=merchant.website,
        created_at=merchant.created_at,
        updated_at=merchant.updated_at,
        transaction_count=stats.transaction_count or 0,
        store_count=stats.store_count or 0,
        total_spent=float(stats.total_spent or 0)
    )


@router.patch("/{merchant_id}", response_model=MerchantSchema)
def update_merchant(
    merchant_id: UUID,
    merchant_update: MerchantUpdate,
    db: Session = Depends(get_db),
):
    """Update a merchant."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Update fields
    for field, value in merchant_update.model_dump(exclude_unset=True).items():
        setattr(merchant, field, value)

    db.commit()
    db.refresh(merchant)

    return merchant


@router.delete("/{merchant_id}", status_code=204)
def delete_merchant(
    merchant_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a merchant."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    db.delete(merchant)
    db.commit()

    return None


# ============================================
# Store Endpoints
# ============================================

@router.get("/{merchant_id}/stores", response_model=StoreListResponse)
def list_merchant_stores(
    merchant_id: UUID,
    db: Session = Depends(get_db),
):
    """List all stores for a specific merchant."""
    user = get_default_user(db)

    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Get stores with stats
    stores = db.query(
        Store,
        func.count(Transaction.id).label('transaction_count'),
        func.sum(Transaction.amount).label('total_spent')
    ).outerjoin(
        Transaction,
        (Transaction.store_id == Store.id) &
        (Transaction.user_id == user.id)
    ).filter(
        Store.merchant_id == merchant_id
    ).group_by(Store.id).all()

    store_list = [
        StoreWithStats(
            id=store.id,
            merchant_id=store.merchant_id,
            store_identifier=store.store_identifier,
            store_name=store.store_name,
            address=store.address,
            city=store.city,
            postal_code=store.postal_code,
            country=store.country,
            latitude=float(store.latitude) if store.latitude else None,
            longitude=float(store.longitude) if store.longitude else None,
            notes=store.notes,
            created_at=store.created_at,
            updated_at=store.updated_at,
            merchant=merchant,
            transaction_count=count or 0,
            total_spent=float(spent or 0)
        )
        for store, count, spent in stores
    ]

    return StoreListResponse(stores=store_list, total=len(store_list))


@router.post("/{merchant_id}/stores", response_model=StoreSchema, status_code=201)
def create_store(
    merchant_id: UUID,
    store: StoreCreate,
    db: Session = Depends(get_db),
):
    """Create a new store for a merchant."""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Check if store already exists
    existing = db.query(Store).filter(
        Store.merchant_id == merchant_id,
        Store.store_identifier == store.store_identifier
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Store with identifier '{store.store_identifier}' already exists for this merchant"
        )

    db_store = Store(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)

    return db_store
