"""Auto-tagging service for transactions."""
from typing import List, Set, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import Transaction, Tag


class AutoTagger:
    """
    Automatically suggests tags for transactions based on:
    - Merchant name
    - Transaction amount
    - Operation type
    - Keywords in title
    """

    # Merchant to tag mappings
    MERCHANT_TAGS = {
        'żabka': ['grocery', 'convenience-store', 'shopping'],
        'biedronka': ['grocery', 'shopping'],
        'lidl': ['grocery', 'shopping'],
        'carrefour': ['grocery', 'shopping'],
        'rossmann': ['personal-care', 'shopping'],
        'decathlon': ['sports', 'shopping'],
        'reserved': ['clothing', 'shopping'],
        'zara': ['clothing', 'shopping'],
        'h&m': ['clothing', 'shopping'],
        'uber': ['transport', 'taxi'],
        'bolt': ['transport', 'taxi'],
        'orlen': ['fuel', 'transport'],
        'shell': ['fuel', 'transport'],
        'bp': ['fuel', 'transport'],
        'mcdonald': ['food', 'fast-food', 'dining'],
        'kfc': ['food', 'fast-food', 'dining'],
        'starbucks': ['food', 'coffee', 'dining'],
        'costa': ['food', 'coffee', 'dining'],
        'piekarnia': ['food', 'bakery'],
        'caffe': ['food', 'coffee', 'dining'],
        'helios': ['entertainment', 'cinema'],
        'cinema': ['entertainment', 'cinema'],
        'kino': ['entertainment', 'cinema'],
        'medicover': ['health', 'medical'],
        'apteka': ['health', 'pharmacy'],
    }

    # Operation type mappings
    OPERATION_TAGS = {
        'zakup przy użyciu karty': ['card-payment'],
        'przelew': ['transfer'],
        'wypłata z bankomatu': ['cash-withdrawal', 'atm'],
        'blik': ['blik', 'mobile-payment'],
        'płatność': ['payment'],
    }

    # Keyword-based tags
    KEYWORD_TAGS = {
        'parking': ['transport', 'parking'],
        'hotel': ['accommodation', 'travel'],
        'airbnb': ['accommodation', 'travel'],
        'booking': ['travel'],
        'warszawa': ['warsaw'],
        'kraków': ['krakow'],
        'wrocław': ['wroclaw'],
        'gdańsk': ['gdansk'],
        'salary': ['income', 'salary'],
        'wynagrodzenie': ['income', 'salary'],
        'netflix': ['subscription', 'entertainment'],
        'spotify': ['subscription', 'entertainment'],
        'internet': ['subscription', 'utilities'],
        'energia': ['utilities', 'electricity'],
        'gaz': ['utilities', 'gas'],
        'woda': ['utilities', 'water'],
    }

    def __init__(self, db: Session, user_id: UUID):
        """
        Initialize auto-tagger.

        Args:
            db: Database session
            user_id: User UUID
        """
        self.db = db
        self.user_id = user_id

    def suggest_tags(self, transaction: Transaction) -> List[str]:
        """
        Suggest tags for a transaction.

        Args:
            transaction: Transaction to analyze

        Returns:
            List of suggested tag names (normalized)
        """
        suggested_tags: Set[str] = set()

        # 1. Merchant-based tags
        if transaction.normalized_merchant_name:
            merchant_lower = transaction.normalized_merchant_name.lower()
            for merchant_key, tags in self.MERCHANT_TAGS.items():
                if merchant_key in merchant_lower:
                    suggested_tags.update(tags)

        # 2. Operation type tags
        operation_lower = transaction.operation_type.lower()
        for op_key, tags in self.OPERATION_TAGS.items():
            if op_key in operation_lower:
                suggested_tags.update(tags)

        # 3. Keyword-based tags from title
        title_lower = transaction.title.lower()
        for keyword, tags in self.KEYWORD_TAGS.items():
            if keyword in title_lower:
                suggested_tags.update(tags)

        # 4. Amount-based tags
        amount = float(transaction.amount)
        if amount < 0:  # Expense
            suggested_tags.add('expense')
            if abs(amount) > 500:
                suggested_tags.add('major-expense')
            elif abs(amount) < 20:
                suggested_tags.add('small-purchase')
        else:  # Income
            suggested_tags.add('income')

        # 5. Location-based tags
        if transaction.location_extracted:
            location_lower = transaction.location_extracted.lower()
            for loc_key, tags in self.KEYWORD_TAGS.items():
                if loc_key in location_lower:
                    suggested_tags.update(tags)

        return list(suggested_tags)

    def get_or_create_tag(self, tag_name: str) -> Tag:
        """
        Get existing tag or create a new one.

        Args:
            tag_name: Tag name (normalized)

        Returns:
            Tag object
        """
        # Normalize tag name (lowercase, hyphens)
        normalized_name = tag_name.lower().strip()
        display_name = normalized_name.replace('-', ' ').title()

        # Check if tag exists
        tag = self.db.query(Tag).filter(
            Tag.user_id == self.user_id,
            Tag.name == normalized_name
        ).first()

        if tag:
            return tag

        # Create new tag
        tag = Tag(
            user_id=self.user_id,
            name=normalized_name,
            display_name=display_name,
            color=self._get_color_for_tag(normalized_name)
        )
        self.db.add(tag)
        self.db.flush()

        return tag

    def _get_color_for_tag(self, tag_name: str) -> str:
        """
        Get a color for a tag based on its category.

        Args:
            tag_name: Tag name

        Returns:
            Hex color code
        """
        color_map = {
            'food': '#f59e0b',      # Orange
            'grocery': '#10b981',   # Green
            'shopping': '#8b5cf6',  # Purple
            'transport': '#3b82f6', # Blue
            'health': '#ef4444',    # Red
            'entertainment': '#ec4899',  # Pink
            'income': '#22c55e',    # Light green
            'expense': '#dc2626',   # Dark red
            'utilities': '#6366f1', # Indigo
            'subscription': '#a855f7',  # Purple
            'travel': '#14b8a6',    # Teal
        }

        # Find category in tag name
        for category, color in color_map.items():
            if category in tag_name:
                return color

        # Default color
        return '#6b7280'  # Gray
