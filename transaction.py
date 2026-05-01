"""
Transaction module for business blockchain.
Defines transaction structure and validation.
"""

import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Transaction:
    """
    Business transaction record.
    All fields are encrypted within the block.
    """
    transaction_type: str          # e.g., "payment", "invoice", "expense", "transfer"
    amount: float
    currency: str = "USD"
    description: str = ""
    from_account: str = ""
    to_account: str = ""
    reference_id: str = ""         # External reference (invoice #, receipt #, etc.)
    metadata: dict = field(default_factory=dict)  # Additional business data
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create Transaction from dictionary."""
        return cls(**data)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> 'Transaction':
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def get_hash(self) -> str:
        """Get SHA-256 hash of transaction data."""
        return hashlib.sha256(self.to_json().encode()).hexdigest()

    def validate(self) -> tuple:
        """
        Validate transaction fields.
        Returns (is_valid, error_message).
        """
        if not self.transaction_type:
            return False, "Transaction type is required"

        if self.amount <= 0:
            return False, "Amount must be positive"

        if not self.currency:
            return False, "Currency is required"

        valid_types = ["payment", "invoice", "expense", "transfer", "refund", "adjustment"]
        if self.transaction_type not in valid_types:
            return False, f"Invalid transaction type. Must be one of: {valid_types}"

        return True, ""


def create_transaction(
    transaction_type: str,
    amount: float,
    currency: str = "USD",
    description: str = "",
    from_account: str = "",
    to_account: str = "",
    reference_id: str = "",
    metadata: dict = None
) -> Transaction:
    """Helper function to create a new transaction."""
    return Transaction(
        transaction_type=transaction_type,
        amount=amount,
        currency=currency,
        description=description,
        from_account=from_account,
        to_account=to_account,
        reference_id=reference_id,
        metadata=metadata or {}
    )
