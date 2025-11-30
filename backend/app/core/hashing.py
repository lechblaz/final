"""Hashing utilities for file and transaction deduplication."""
import hashlib
from datetime import date
from typing import Union


def compute_file_hash(content: bytes) -> str:
    """
    Compute SHA256 hash of file content for duplicate detection.

    Args:
        content: File content as bytes

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content).hexdigest()


def compute_transaction_hash(
    user_id: str,
    booking_date: Union[date, str],
    transaction_date: Union[date, str],
    amount: float,
    title: str
) -> str:
    """
    Compute SHA256 hash of transaction for duplicate detection.

    Args:
        user_id: User UUID
        booking_date: Booking date
        transaction_date: Transaction date
        amount: Transaction amount
        title: Transaction title/description

    Returns:
        Hexadecimal hash string
    """
    # Convert dates to strings if needed
    booking_str = booking_date.isoformat() if isinstance(booking_date, date) else str(booking_date)
    transaction_str = transaction_date.isoformat() if isinstance(transaction_date, date) else str(transaction_date)

    # Create hash input
    hash_input = f"{user_id}|{booking_str}|{transaction_str}|{amount}|{title}"

    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
