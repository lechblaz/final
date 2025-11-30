"""mBank CSV parser for Polish bank statements."""
import csv
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from io import StringIO


class MBankCSVParser:
    """
    Parser for mBank CSV export format.

    Handles:
    - Windows-1250 encoding (Polish characters)
    - Multi-section CSV structure
    - Metadata extraction
    - Transaction parsing with type conversion
    """

    TRANSACTION_START_LINE = 38  # 0-indexed: line 39 in file
    ENCODING = 'windows-1250'
    DELIMITER = ';'

    def __init__(self, file_content: bytes):
        """
        Initialize parser with raw file bytes.

        Args:
            file_content: Raw CSV file content as bytes
        """
        self.raw_content = file_content
        self.decoded_content = file_content.decode(self.ENCODING)
        self.lines = self.decoded_content.split('\n')

    def parse(self) -> Dict[str, any]:
        """
        Parse entire CSV into structured data.

        Returns:
            Dictionary with metadata, summary, and transactions
        """
        return {
            "metadata": self._parse_metadata(),
            "summary": self._parse_summary(),
            "transactions": self._parse_transactions()
        }

    def _parse_metadata(self) -> Dict[str, str]:
        """Extract account metadata from header section."""
        metadata = {}

        for i, line in enumerate(self.lines[:37]):
            if line.startswith('#Klient'):
                # Next line contains client name
                if i + 1 < len(self.lines):
                    metadata['client_name'] = self.lines[i + 1].strip()

            elif line.startswith('#Za okres:'):
                parts = line.split(';')
                if len(parts) >= 3:
                    metadata['period_start'] = self._parse_date(parts[1])
                    metadata['period_end'] = self._parse_date(parts[2])

            elif line.startswith('#Rodzaj rachunku'):
                if i + 1 < len(self.lines):
                    metadata['account_type'] = self.lines[i + 1].strip().rstrip(';')

            elif line.startswith('#Waluta'):
                if i + 1 < len(self.lines):
                    metadata['currency'] = self.lines[i + 1].strip().rstrip(';')

            elif line.startswith('#Numer rachunku'):
                if i + 1 < len(self.lines):
                    account_num = self.lines[i + 1].strip().rstrip(';').replace(' ', '')
                    metadata['account_number'] = account_num

            elif line.startswith('#Saldo początkowe'):
                parts = line.split(';')
                if len(parts) >= 2:
                    metadata['opening_balance'] = self._parse_amount(parts[1])

        return metadata

    def _parse_summary(self) -> Dict[str, any]:
        """Extract summary statistics from CSV."""
        summary = {}

        for i, line in enumerate(self.lines):
            if line.startswith('#Podsumowanie obrotów'):
                # Next 3 lines: Credits, Debits, Total
                if i + 3 < len(self.lines):
                    credits_line = self.lines[i + 1].split(';')
                    debits_line = self.lines[i + 2].split(';')
                    total_line = self.lines[i + 3].split(';')

                    if len(credits_line) >= 3:
                        summary['credits_count'] = int(credits_line[1])
                        summary['credits_amount'] = self._parse_amount(credits_line[2])

                    if len(debits_line) >= 3:
                        summary['debits_count'] = int(debits_line[1])
                        summary['debits_amount'] = self._parse_amount(debits_line[2])

                    if len(total_line) >= 3:
                        summary['total_count'] = int(total_line[1])
                        summary['total_amount'] = self._parse_amount(total_line[2])
                break

        return summary

    def _parse_transactions(self) -> List[Dict[str, any]]:
        """Parse transaction rows from CSV."""
        transactions = []

        # Start from line 39 (index 38)
        if len(self.lines) <= self.TRANSACTION_START_LINE:
            return transactions

        transaction_lines = self.lines[self.TRANSACTION_START_LINE:]

        reader = csv.reader(
            transaction_lines,
            delimiter=self.DELIMITER,
            quotechar='"'
        )

        try:
            # Skip header row
            next(reader)
        except StopIteration:
            return transactions

        for row in reader:
            # Stop at footer (empty lines or lines starting with #)
            if len(row) < 8:
                break

            if not row[0] or row[0].startswith('#'):
                break

            transaction = self._parse_transaction_row(row)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _parse_transaction_row(self, row: List[str]) -> Optional[Dict[str, any]]:
        """
        Parse single transaction row.

        Row structure:
        [0] Booking date
        [1] Transaction date
        [2] Operation type
        [3] Title/Description
        [4] Sender/Recipient
        [5] Account number
        [6] Amount
        [7] Balance after
        """
        try:
            transaction = {
                "booking_date": self._parse_date(row[0]),
                "transaction_date": self._parse_date(row[1]),
                "operation_type": row[2].strip(),
                "title": self._clean_title(row[3]),
                "sender_recipient": row[4].strip(),
                "account_number": row[5].strip().replace("'", ""),
                "amount": self._parse_amount(row[6]),
                "balance_after": self._parse_amount(row[7]),
                "raw_title": row[3]  # Keep original for reference
            }

            # Validate required fields
            if transaction["booking_date"] is None or transaction["amount"] is None:
                return None

            return transaction

        except Exception as e:
            # Log error but continue parsing
            print(f"Error parsing transaction row: {row[:3]}..., error: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime.

        Handles formats:
        - 2025-08-01 (ISO)
        - 01.08.2025 (Polish)
        """
        if not date_str or date_str.strip() == '':
            return None

        date_str = date_str.strip()

        try:
            if '-' in date_str:
                return datetime.strptime(date_str, '%Y-%m-%d')
            elif '.' in date_str:
                return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            return None

        return None

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse amount string to float.

        Handles:
        - Comma as decimal separator: 16,43
        - Space as thousands separator: 1 113,28
        - Currency symbols: PLN
        """
        if not amount_str or amount_str.strip() == '':
            return None

        # Remove currency symbols and spaces
        amount_str = amount_str.replace('PLN', '').replace(' ', '').strip()

        # Replace comma with dot (Polish decimal separator)
        amount_str = amount_str.replace(',', '.')

        try:
            return float(amount_str)
        except ValueError:
            return None

    def _clean_title(self, title: str) -> str:
        """
        Clean transaction title.

        Example:
        'ZABKA Z1748 K.1    /WARSZAWA    DATA TRANSAKCJI: 2025-07-31'
        -> 'ZABKA Z1748 K.1 /WARSZAWA'
        """
        # Remove transaction date suffix
        if 'DATA TRANSAKCJI:' in title:
            title = title.split('DATA TRANSAKCJI:')[0]

        # Remove excessive whitespace
        title = ' '.join(title.split())

        return title.strip()

    def compute_file_hash(self) -> str:
        """Compute SHA256 hash of file for duplicate detection."""
        return hashlib.sha256(self.raw_content).hexdigest()
