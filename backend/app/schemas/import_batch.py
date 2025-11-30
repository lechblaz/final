"""Import batch schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class ImportBatch(BaseModel):
    """Schema for import batch response."""
    id: UUID
    user_id: UUID
    file_name: str
    file_hash: str
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    currency: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    transactions_imported: int
    duplicates_skipped: int
    import_status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImportBatchList(BaseModel):
    """Schema for paginated import batch list."""
    imports: List[ImportBatch]
    total: int
