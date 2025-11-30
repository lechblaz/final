"""Merchant extraction service for parsing transaction titles."""
import re
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class MerchantInfo:
    """Extracted merchant information from transaction title."""
    merchant_name: Optional[str] = None
    store_identifier: Optional[str] = None
    location_extracted: Optional[str] = None
    raw_merchant_text: str = ""
    confidence: float = 0.0


class MerchantExtractor:
    """
    Extracts merchant details from Polish bank transaction titles.

    Common patterns:
    - "ZABKA Z1748 K.2 /WARSZAWA" -> merchant: Żabka, store: Z1748 K.2, location: Warszawa
    - "ROSSMANN 129 /Warszawa" -> merchant: Rossmann, store: 129, location: Warszawa
    - "DECATHLON WARSZAWA /WARSZAWA" -> merchant: Decathlon, location: Warszawa
    - "KINO WISLA /WARSZAWA" -> merchant: Kino Wisła, location: Warszawa
    """

    # Known merchant name mappings (uppercase -> proper name)
    MERCHANT_MAPPINGS = {
        'ZABKA': 'Żabka',
        'BIEDRONKA': 'Biedronka',
        'ROSSMANN': 'Rossmann',
        'DECATHLON': 'Decathlon',
        'LIDL': 'Lidl',
        'AUCHAN': 'Auchan',
        'CARREFOUR': 'Carrefour',
        'KAUFLAND': 'Kaufland',
        'ZARA': 'Zara',
        'H&M': 'H&M',
        'RESERVED': 'Reserved',
        'HELIOS': 'Helios',
        'CINEMA CITY': 'Cinema City',
        'MEDICOVER': 'Medicover',
        'ORLEN': 'Orlen',
        'SHELL': 'Shell',
        'BP': 'BP',
        'MCDONALD': 'McDonald\'s',
        'KFC': 'KFC',
        'STARBUCKS': 'Starbucks',
        'COSTA COFFEE': 'Costa Coffee',
        'GREEN CAFFE NERO': 'Green Caffè Nero',
    }

    def extract(self, title: str) -> MerchantInfo:
        """
        Extract merchant information from transaction title.

        Args:
            title: Raw transaction title from bank statement

        Returns:
            MerchantInfo with extracted data
        """
        if not title:
            return MerchantInfo(raw_merchant_text=title or "", confidence=0.0)

        # Store original
        info = MerchantInfo(raw_merchant_text=title)

        # Try to extract location (usually after /)
        location_match = re.search(r'/\s*([A-Za-zęóąśłżźćńĘÓĄŚŁŻŹĆŃ\s-]+)(?:\s*$|/)', title)
        if location_match:
            info.location_extracted = location_match.group(1).strip()

        # Extract merchant name and store identifier
        # Pattern 1: "ZABKA Z1748 K.2 /WARSZAWA"
        pattern1 = re.match(
            r'^([A-Z&\s]+?)\s+([A-Z0-9]+(?:\s+[A-Z0-9.]+)?)\s*/.*',
            title
        )
        if pattern1:
            merchant_raw = pattern1.group(1).strip()
            info.store_identifier = pattern1.group(2).strip()
            info.merchant_name = self._normalize_merchant_name(merchant_raw)
            info.confidence = 0.9
            return info

        # Pattern 2: "ROSSMANN 129 /Warszawa" (just number)
        pattern2 = re.match(
            r'^([A-Z&\s]+?)\s+(\d+)\s*/.*',
            title
        )
        if pattern2:
            merchant_raw = pattern2.group(1).strip()
            info.store_identifier = pattern2.group(2).strip()
            info.merchant_name = self._normalize_merchant_name(merchant_raw)
            info.confidence = 0.9
            return info

        # Pattern 3: "DECATHLON WARSZAWA /WARSZAWA" (no store number)
        pattern3 = re.match(
            r'^([A-Z&\s]+?)\s+[A-Za-zęóąśłżźćń]+\s*/.*',
            title
        )
        if pattern3:
            merchant_raw = pattern3.group(1).strip()
            info.merchant_name = self._normalize_merchant_name(merchant_raw)
            info.confidence = 0.8
            return info

        # Pattern 4: Just merchant name with location
        pattern4 = re.match(
            r'^([A-Za-zęóąśłżźćńĘÓĄŚŁŻŹĆŃ\s&.-]+?)\s*/.*',
            title
        )
        if pattern4:
            merchant_raw = pattern4.group(1).strip()
            info.merchant_name = self._normalize_merchant_name(merchant_raw)
            info.confidence = 0.7
            return info

        # Pattern 5: No slash, try to extract merchant from start
        pattern5 = re.match(
            r'^([A-Za-zęóąśłżźćńĘÓĄŚŁŻŹĆŃ\s&.-]+)',
            title
        )
        if pattern5:
            merchant_raw = pattern5.group(1).strip()
            info.merchant_name = self._normalize_merchant_name(merchant_raw)
            info.confidence = 0.5
            return info

        # Fallback: use entire title
        info.merchant_name = title.strip()
        info.confidence = 0.3
        return info

    def _normalize_merchant_name(self, raw_name: str) -> str:
        """
        Normalize merchant name to proper capitalization.

        Args:
            raw_name: Raw merchant name (usually uppercase)

        Returns:
            Normalized merchant name
        """
        # Check if we have a known mapping
        upper_name = raw_name.upper().strip()

        for key, value in self.MERCHANT_MAPPINGS.items():
            if key in upper_name:
                return value

        # Convert to title case for unknown merchants
        # Handle Polish characters properly
        words = raw_name.split()
        normalized_words = []

        for word in words:
            # Keep acronyms uppercase
            if len(word) <= 3 and word.isupper():
                normalized_words.append(word)
            # Keep special patterns
            elif '.' in word or '&' in word:
                normalized_words.append(word)
            else:
                # Title case
                normalized_words.append(word.title())

        return ' '.join(normalized_words)
