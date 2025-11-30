"""Tag API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from uuid import UUID

from app.database import get_db
from app.models import Tag, TransactionTag, Transaction, User
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    Tag as TagSchema,
    TagWithStats,
    TagListResponse,
    TransactionTagCreate,
    TransactionTagsUpdate,
)
from app.services.auto_tagger import AutoTagger

router = APIRouter(prefix="/tags", tags=["tags"])


def get_default_user(db: Session) -> User:
    """Get default user for MVP (single-user mode)."""
    user = db.query(User).filter(User.email == "default@finance.local").first()
    if not user:
        raise HTTPException(status_code=500, detail="Default user not found")
    return user


# ============================================
# Tag Management Endpoints
# ============================================

@router.get("", response_model=TagListResponse)
def list_tags(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all tags with usage statistics.

    Returns tags sorted by usage count.
    """
    user = get_default_user(db)

    query = db.query(Tag).filter(Tag.user_id == user.id)

    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Tag.display_name.ilike(search_pattern)) |
            (Tag.name.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    tags = query.order_by(desc(Tag.usage_count)).offset(offset).limit(limit).all()

    # Convert to response format with stats
    tag_list = [
        TagWithStats(
            id=tag.id,
            name=tag.name,
            display_name=tag.display_name,
            color=tag.color,
            icon=tag.icon,
            description=tag.description,
            usage_count=tag.usage_count,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
            transaction_count=tag.usage_count  # Same as usage_count for now
        )
        for tag in tags
    ]

    return TagListResponse(tags=tag_list, total=total)


@router.post("", response_model=TagSchema, status_code=201)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
):
    """Create a new tag."""
    user = get_default_user(db)

    # Normalize tag name
    normalized_name = tag.name.lower().strip()

    # Check if tag already exists
    existing = db.query(Tag).filter(
        Tag.user_id == user.id,
        Tag.name == normalized_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Tag with name '{normalized_name}' already exists"
        )

    db_tag = Tag(
        user_id=user.id,
        name=normalized_name,
        display_name=tag.display_name or tag.name.title(),
        color=tag.color or '#6b7280',
        icon=tag.icon,
        description=tag.description
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    return db_tag


@router.get("/{tag_id}", response_model=TagWithStats)
def get_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific tag with statistics."""
    user = get_default_user(db)

    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == user.id
    ).first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    return TagWithStats(
        id=tag.id,
        name=tag.name,
        display_name=tag.display_name,
        color=tag.color,
        icon=tag.icon,
        description=tag.description,
        usage_count=tag.usage_count,
        created_at=tag.created_at,
        updated_at=tag.updated_at,
        transaction_count=tag.usage_count
    )


@router.patch("/{tag_id}", response_model=TagSchema)
def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
):
    """Update a tag."""
    user = get_default_user(db)

    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == user.id
    ).first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Update fields
    for field, value in tag_update.model_dump(exclude_unset=True).items():
        setattr(tag, field, value)

    db.commit()
    db.refresh(tag)

    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a tag."""
    user = get_default_user(db)

    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == user.id
    ).first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()

    return None


# ============================================
# Transaction Tagging Endpoints
# ============================================

@router.post("/apply", status_code=200)
def apply_tags_to_transaction(
    transaction_id: UUID,
    tags_update: TransactionTagsUpdate,
    db: Session = Depends(get_db),
):
    """
    Apply tags to a transaction.

    Replaces existing tags with the new set.
    """
    user = get_default_user(db)

    # Get transaction
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Remove existing tags
    db.query(TransactionTag).filter(
        TransactionTag.transaction_id == transaction_id
    ).delete()

    # Add new tags
    for tag_id in tags_update.tag_ids:
        # Verify tag exists and belongs to user
        tag = db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.user_id == user.id
        ).first()

        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

        # Create transaction-tag association
        transaction_tag = TransactionTag(
            transaction_id=transaction_id,
            tag_id=tag_id,
            source='manual',
            confidence=1.0
        )
        db.add(transaction_tag)

        # Update tag usage count
        tag.usage_count = db.query(func.count(TransactionTag.id)).filter(
            TransactionTag.tag_id == tag_id
        ).scalar()

    db.commit()

    return {"status": "success", "tag_count": len(tags_update.tag_ids)}


@router.get("/suggest/{transaction_id}")
def suggest_tags_for_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Suggest tags for a transaction based on auto-tagging rules.

    Returns suggested tag names that can be created/applied.
    """
    user = get_default_user(db)

    # Get transaction
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Get auto-tagger
    auto_tagger = AutoTagger(db, user.id)

    # Get suggestions
    suggested_tag_names = auto_tagger.suggest_tags(transaction)

    # Get or create tags
    suggested_tags = []
    for tag_name in suggested_tag_names:
        tag = auto_tagger.get_or_create_tag(tag_name)
        suggested_tags.append({
            "id": str(tag.id),
            "name": tag.name,
            "display_name": tag.display_name,
            "color": tag.color
        })

    db.commit()

    return {
        "transaction_id": str(transaction_id),
        "suggested_tags": suggested_tags
    }


@router.post("/auto-tag-all", status_code=200)
def auto_tag_all_transactions(
    db: Session = Depends(get_db),
):
    """
    Auto-tag all untagged transactions.

    This is useful for initially populating tags on existing transactions.
    """
    user = get_default_user(db)

    # Get all transactions without tags
    transactions = db.query(Transaction).outerjoin(TransactionTag).filter(
        Transaction.user_id == user.id,
        TransactionTag.id.is_(None)
    ).all()

    auto_tagger = AutoTagger(db, user.id)
    tagged_count = 0

    for transaction in transactions:
        # Get suggestions
        suggested_tag_names = auto_tagger.suggest_tags(transaction)

        # Apply tags
        for tag_name in suggested_tag_names:
            tag = auto_tagger.get_or_create_tag(tag_name)

            # Create transaction-tag association
            transaction_tag = TransactionTag(
                transaction_id=transaction.id,
                tag_id=tag.id,
                source='auto',
                confidence=0.85
            )
            db.add(transaction_tag)

        if suggested_tag_names:
            tagged_count += 1

    # Update tag usage counts
    tags = db.query(Tag).filter(Tag.user_id == user.id).all()
    for tag in tags:
        tag.usage_count = db.query(func.count(TransactionTag.id)).filter(
            TransactionTag.tag_id == tag.id
        ).scalar()

    db.commit()

    return {
        "status": "success",
        "transactions_tagged": tagged_count,
        "total_transactions": len(transactions)
    }
