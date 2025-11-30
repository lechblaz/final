"""Dashboard API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Dict, Any
from decimal import Decimal

from app.database import get_db
from app.models import Transaction as TransactionModel, TransactionTag, Tag, User

router = APIRouter()


def get_default_user(db: Session) -> User:
    """Get default user for MVP."""
    user = db.query(User).filter(User.email == 'default@finance.local').first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Default user not found")
    return user


@router.get("/dashboard/sankey")
async def get_sankey_data(db: Session = Depends(get_db)):
    """
    Get Sankey diagram data for income/expense flow through tags.

    Returns:
        Dictionary with nodes and links for Sankey diagram
    """
    user = get_default_user(db)

    # Get income and expense totals
    income_expenses = db.query(
        case(
            (TransactionModel.amount >= 0, 'Income'),
            else_='Expense'
        ).label('type'),
        func.sum(func.abs(TransactionModel.amount)).label('total')
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False
    ).group_by('type').all()

    income_total = Decimal('0')
    expense_total = Decimal('0')

    for row in income_expenses:
        if row.type == 'Income':
            income_total = row.total or Decimal('0')
        else:
            expense_total = row.total or Decimal('0')

    # Get tag totals for expenses (negative amounts)
    expense_tags = db.query(
        Tag.id,
        Tag.name,
        Tag.display_name,
        Tag.color,
        func.sum(func.abs(TransactionModel.amount)).label('total')
    ).join(
        TransactionTag,
        TransactionTag.tag_id == Tag.id
    ).join(
        TransactionModel,
        TransactionModel.id == TransactionTag.transaction_id
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False,
        TransactionModel.amount < 0,  # Only expenses
        Tag.name != 'expense',  # Exclude generic expense tag
        Tag.name != 'income'    # Exclude income tag
    ).group_by(
        Tag.id,
        Tag.name,
        Tag.display_name,
        Tag.color
    ).order_by(
        func.sum(func.abs(TransactionModel.amount)).desc()
    ).limit(15).all()  # Top 15 expense tags

    # Get tag totals for income (positive amounts)
    income_tags = db.query(
        Tag.id,
        Tag.name,
        Tag.display_name,
        Tag.color,
        func.sum(TransactionModel.amount).label('total')
    ).join(
        TransactionTag,
        TransactionTag.tag_id == Tag.id
    ).join(
        TransactionModel,
        TransactionModel.id == TransactionTag.transaction_id
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False,
        TransactionModel.amount > 0,  # Only income
        Tag.name != 'income',   # Exclude generic income tag
        Tag.name != 'expense'   # Exclude expense tag
    ).group_by(
        Tag.id,
        Tag.name,
        Tag.display_name,
        Tag.color
    ).order_by(
        func.sum(TransactionModel.amount).desc()
    ).limit(10).all()  # Top 10 income tags

    # Build nodes
    nodes = [
        {"id": "income", "name": "Income"},
        {"id": "expense", "name": "Expenses"}
    ]

    # Add income tag nodes
    for tag in income_tags:
        nodes.append({
            "id": f"income_{tag.name}",
            "name": tag.display_name,
            "color": tag.color
        })

    # Add expense tag nodes
    for tag in expense_tags:
        nodes.append({
            "id": f"expense_{tag.name}",
            "name": tag.display_name,
            "color": tag.color
        })

    # Build links
    links = []

    # Income source -> income tags
    for tag in income_tags:
        links.append({
            "source": "income",
            "target": f"income_{tag.name}",
            "value": float(tag.total)
        })

    # Income tags -> expense (showing where income goes)
    # For simplicity, we'll show proportional flow from income to expenses
    if income_tags and expense_total > 0:
        for tag in income_tags:
            proportion = float(tag.total) / float(income_total) if income_total > 0 else 0
            links.append({
                "source": f"income_{tag.name}",
                "target": "expense",
                "value": float(expense_total * Decimal(str(proportion)))
            })

    # Expense -> expense tag categories
    for tag in expense_tags:
        links.append({
            "source": "expense",
            "target": f"expense_{tag.name}",
            "value": float(tag.total)
        })

    return {
        "nodes": nodes,
        "links": links,
        "totals": {
            "income": float(income_total),
            "expense": float(expense_total),
            "balance": float(income_total - expense_total)
        }
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get dashboard summary statistics.

    Returns:
        Summary statistics including totals, top categories, etc.
    """
    user = get_default_user(db)

    # Get total transactions count
    total_transactions = db.query(func.count(TransactionModel.id)).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False
    ).scalar()

    # Get income/expense totals
    income = db.query(
        func.sum(TransactionModel.amount)
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False,
        TransactionModel.amount > 0
    ).scalar() or Decimal('0')

    expense = db.query(
        func.sum(func.abs(TransactionModel.amount))
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False,
        TransactionModel.amount < 0
    ).scalar() or Decimal('0')

    # Get top expense categories
    top_expenses = db.query(
        Tag.display_name,
        Tag.color,
        func.sum(func.abs(TransactionModel.amount)).label('total')
    ).join(
        TransactionTag,
        TransactionTag.tag_id == Tag.id
    ).join(
        TransactionModel,
        TransactionModel.id == TransactionTag.transaction_id
    ).filter(
        TransactionModel.user_id == user.id,
        TransactionModel.is_hidden == False,
        TransactionModel.amount < 0,
        Tag.name != 'expense'
    ).group_by(
        Tag.display_name,
        Tag.color
    ).order_by(
        func.sum(func.abs(TransactionModel.amount)).desc()
    ).limit(5).all()

    return {
        "total_transactions": total_transactions,
        "income": float(income),
        "expense": float(expense),
        "balance": float(income - expense),
        "top_expenses": [
            {
                "category": cat.display_name,
                "color": cat.color,
                "amount": float(cat.total)
            }
            for cat in top_expenses
        ]
    }
