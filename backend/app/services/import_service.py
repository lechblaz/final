"""Import service for CSV files."""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import ImportBatch, Transaction, User
from app.services.csv_parser import MBankCSVParser
from app.core.hashing import compute_transaction_hash


class ImportService:
    """Service for importing CSV bank statements."""

    def __init__(self, db: Session, user_id: UUID):
        """
        Initialize import service.

        Args:
            db: Database session
            user_id: User UUID
        """
        self.db = db
        self.user_id = user_id

    async def import_mbank_csv(
        self,
        file_content: bytes,
        file_name: str
    ) -> ImportBatch:
        """
        Import mBank CSV file.

        Args:
            file_content: Raw CSV file bytes
            file_name: Original filename

        Returns:
            ImportBatch with statistics

        Raises:
            ValueError: If file already imported
        """
        # Step 1: Parse CSV
        parser = MBankCSVParser(file_content)
        data = parser.parse()
        file_hash = parser.compute_file_hash()

        # Step 2: Check for duplicate file
        existing_import = self.db.query(ImportBatch).filter(
            ImportBatch.user_id == self.user_id,
            ImportBatch.file_hash == file_hash
        ).first()

        if existing_import:
            raise ValueError(
                f"File already imported on {existing_import.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

        # Step 3: Create import batch
        import_batch = ImportBatch(
            user_id=self.user_id,
            file_name=file_name,
            file_hash=file_hash,
            account_number=data['metadata'].get('account_number'),
            account_type=data['metadata'].get('account_type'),
            currency=data['metadata'].get('currency', 'PLN'),
            period_start=data['metadata'].get('period_start'),
            period_end=data['metadata'].get('period_end'),
            raw_content=parser.decoded_content,
            import_status='processing'
        )
        self.db.add(import_batch)
        self.db.flush()  # Get import_batch.id

        # Step 4: Import transactions
        imported_count = 0
        duplicate_count = 0
        seen_hashes = set()  # Track hashes in current import to handle intra-file duplicates

        for txn_data in data['transactions']:
            # Compute transaction hash
            txn_hash = compute_transaction_hash(
                user_id=str(self.user_id),
                booking_date=txn_data['booking_date'],
                transaction_date=txn_data['transaction_date'],
                amount=txn_data['amount'],
                title=txn_data['title']
            )

            # Check for duplicate transaction (in DB or in current import)
            if txn_hash in seen_hashes:
                duplicate_count += 1
                continue

            existing_txn = self.db.query(Transaction).filter(
                Transaction.transaction_hash == txn_hash
            ).first()

            if existing_txn:
                duplicate_count += 1
                continue

            # Mark as seen for this import session
            seen_hashes.add(txn_hash)

            # Create transaction
            transaction = Transaction(
                user_id=self.user_id,
                import_batch_id=import_batch.id,
                transaction_hash=txn_hash,
                booking_date=txn_data['booking_date'].date(),
                transaction_date=txn_data['transaction_date'].date(),
                operation_type=txn_data['operation_type'],
                title=txn_data['title'],
                sender_recipient=txn_data['sender_recipient'],
                account_number=txn_data['account_number'],
                amount=txn_data['amount'],
                balance_after=txn_data['balance_after'],
                currency=data['metadata'].get('currency', 'PLN')
            )

            self.db.add(transaction)
            imported_count += 1

        # Step 5: Update import batch statistics
        import_batch.transactions_imported = imported_count
        import_batch.duplicates_skipped = duplicate_count
        import_batch.import_status = 'completed'

        self.db.commit()
        self.db.refresh(import_batch)

        # TODO: Step 6: Trigger merchant normalization and auto-tagging
        # This will be implemented in Phase 2 and Phase 4
        # await self._enrich_transactions(import_batch.id)

        return import_batch

    def get_default_user_id(self) -> UUID:
        """
        Get default user ID for MVP (single-user mode).

        Returns:
            Default user UUID
        """
        user = self.db.query(User).filter(
            User.email == 'default@finance.local'
        ).first()

        if not user:
            raise ValueError("Default user not found. Database not initialized properly.")

        return user.id
