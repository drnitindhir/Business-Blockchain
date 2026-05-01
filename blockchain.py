"""
Blockchain core implementation.
Handles block creation, chain integrity, and encrypted storage.
"""

import json
import sqlite3
import base64
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from crypto_core import CryptoManager
from transaction import Transaction


@dataclass
class Block:
    """
    Blockchain block structure.
    Contains encrypted transaction data and cryptographic links.
    """
    index: int
    timestamp: str
    transactions_hash: str      # Merkle-like hash of transactions
    encrypted_data: str         # Base64 encoded encrypted transactions
    nonce: str                  # Base64 encoded nonce for encryption
    previous_hash: str
    current_hash: str           # Hash of block header (unencrypted metadata)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Block':
        return cls(**data)


class Blockchain:
    """
    Private blockchain for business transactions.
    All transaction data is encrypted; only block headers are visible.
    """

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.crypto = CryptoManager()
        self._chain_length = 0
        self._genesis_hash = ""
        self._initialized = False

    def _connect(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_chain(self, password: str) -> bool:
        """
        Initialize a new blockchain with master password.
        Creates genesis block and stores salt for key derivation.
        """
        if self.db_path.exists():
            return False  # Chain already exists

        # Derive master key and generate salt
        salt = self.crypto.set_master_key(password)

        # Create database
        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Create tables
            cursor.execute('''
                CREATE TABLE metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE blocks (
                    block_index INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    transactions_hash TEXT NOT NULL,
                    encrypted_data TEXT NOT NULL,
                    nonce TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL
                )
            ''')

            # Store salt and key verification hash
            master_key = self.crypto.get_master_key()
            cursor.execute(
                'INSERT INTO metadata (key, value) VALUES (?, ?)',
                ('salt', base64.b64encode(salt).decode('ascii'))
            )
            cursor.execute(
                'INSERT INTO metadata (key, value) VALUES (?, ?)',
                ('key_hash', base64.b64encode(master_key).decode('ascii'))
            )
            cursor.execute(
                'INSERT INTO metadata (key, value) VALUES (?, ?)',
                ('created_at', datetime.utcnow().isoformat())
            )

            # Create genesis block
            genesis = self._create_genesis_block()
            cursor.execute(
                '''INSERT INTO blocks
                   (block_index, timestamp, transactions_hash, encrypted_data, nonce,
                    previous_hash, current_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (genesis.index, genesis.timestamp, genesis.transactions_hash,
                 genesis.encrypted_data, genesis.nonce,
                 genesis.previous_hash, genesis.current_hash)
            )

            conn.commit()
            self._initialized = True
            self._chain_length = 1
            self._genesis_hash = genesis.current_hash
            return True

        finally:
            conn.close()

    def unlock(self, password: str) -> tuple:
        """
        Unlock blockchain with master password.
        Returns (success, error_message).
        """
        if not self.db_path.exists():
            return False, "Blockchain does not exist. Initialize first."

        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Get stored salt and key hash
            cursor.execute("SELECT value FROM metadata WHERE key = 'salt'")
            row = cursor.fetchone()
            if not row:
                return False, "Invalid blockchain database"
            stored_salt = base64.b64decode(row['value'])

            cursor.execute("SELECT value FROM metadata WHERE key = 'key_hash'")
            row = cursor.fetchone()
            stored_key_hash = base64.b64decode(row['value'])

            # Derive key from password
            derived_key, _ = self.crypto.derive_key(password, stored_salt)

            # Verify password
            if derived_key != stored_key_hash:
                return False, "Invalid master password"

            # Set master key in crypto manager
            self.crypto._master_key = derived_key

            # Load chain length
            cursor.execute("SELECT MAX(block_index) FROM blocks")
            self._chain_length = cursor.fetchone()[0] + 1

            cursor.execute("SELECT value FROM metadata WHERE key = 'genesis_hash'")
            row = cursor.fetchone()
            if row:
                self._genesis_hash = row['value']
            else:
                # Get from first block
                cursor.execute("SELECT current_hash FROM blocks WHERE block_index = 0")
                self._genesis_hash = cursor.fetchone()[0]

            self._initialized = True
            return True, "Blockchain unlocked"

        finally:
            conn.close()

    def _create_genesis_block(self) -> Block:
        """Create the genesis (first) block."""
        timestamp = datetime.utcnow().isoformat()
        previous_hash = "0" * 64

        # Genesis block has no transactions
        transactions_data = json.dumps({
            'type': 'genesis',
            'message': 'Blockchain initialized',
            'timestamp': timestamp
        }).encode()

        encrypted = self.crypto.encrypt(transactions_data)
        transactions_hash = self.crypto.hash_data(transactions_data)

        # Create block header hash
        header_data = f"0|{timestamp}|{transactions_hash}|{previous_hash}".encode()
        current_hash = self.crypto.hash_data(header_data)

        return Block(
            index=0,
            timestamp=timestamp,
            transactions_hash=transactions_hash,
            encrypted_data=encrypted['ciphertext'],
            nonce=encrypted['nonce'],
            previous_hash=previous_hash,
            current_hash=current_hash
        )

    def _compute_block_hash(self, index: int, timestamp: str,
                            transactions_hash: str, previous_hash: str) -> str:
        """Compute hash of block header."""
        header_data = f"{index}|{timestamp}|{transactions_hash}|{previous_hash}"
        return self.crypto.hash_data(header_data.encode())

    def add_transactions(self, transactions: List[Transaction]) -> Block:
        """
        Add a new block with transactions to the chain.
        Returns the new block.
        """
        if not self._initialized:
            raise ValueError("Blockchain not unlocked")

        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Get previous block hash
            cursor.execute("SELECT current_hash FROM blocks ORDER BY block_index DESC LIMIT 1")
            previous_hash = cursor.fetchone()[0]

            # Serialize and hash transactions
            tx_list = [tx.to_dict() for tx in transactions]
            transactions_json = json.dumps(tx_list, sort_keys=True).encode()
            transactions_hash = self.crypto.hash_data(transactions_json)

            # Encrypt transactions
            encrypted = self.crypto.encrypt(transactions_json)

            # Create new block
            index = self._chain_length
            timestamp = datetime.utcnow().isoformat()
            current_hash = self._compute_block_hash(
                index, timestamp, transactions_hash, previous_hash
            )

            block = Block(
                index=index,
                timestamp=timestamp,
                transactions_hash=transactions_hash,
                encrypted_data=encrypted['ciphertext'],
                nonce=encrypted['nonce'],
                previous_hash=previous_hash,
                current_hash=current_hash
            )

            # Store block
            cursor.execute(
                '''INSERT INTO blocks
                   (block_index, timestamp, transactions_hash, encrypted_data, nonce,
                    previous_hash, current_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (block.index, block.timestamp, block.transactions_hash,
                 block.encrypted_data, block.nonce,
                 block.previous_hash, block.current_hash)
            )

            conn.commit()
            self._chain_length += 1
            return block

        finally:
            conn.close()

    def get_block(self, index: int) -> Optional[Block]:
        """Retrieve a block by index."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blocks WHERE block_index = ?", (index,))
            row = cursor.fetchone()

            if not row:
                return None

            return Block(
                index=row['block_index'],
                timestamp=row['timestamp'],
                transactions_hash=row['transactions_hash'],
                encrypted_data=row['encrypted_data'],
                nonce=row['nonce'],
                previous_hash=row['previous_hash'],
                current_hash=row['current_hash']
            )
        finally:
            conn.close()

    def decrypt_block_transactions(self, block: Block) -> List[Transaction]:
        """
        Decrypt and return transactions from a block.
        Requires blockchain to be unlocked.
        """
        if not self._initialized:
            raise ValueError("Blockchain not unlocked")

        transactions_json = self.crypto.decrypt(
            block.nonce,
            block.encrypted_data
        )

        # Check if genesis block
        data = json.loads(transactions_json.decode())
        if isinstance(data, dict) and data.get('type') == 'genesis':
            return []

        tx_dicts = data if isinstance(data, list) else [data]
        return [Transaction.from_dict(tx) for tx in tx_dicts]

    def verify_chain(self) -> tuple:
        """
        Verify blockchain integrity.
        Returns (is_valid, error_message).
        """
        if not self.db_path.exists():
            return False, "Blockchain does not exist"

        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blocks ORDER BY block_index")
            blocks = cursor.fetchall()

            if not blocks:
                return False, "Blockchain is empty"

            prev_hash = "0" * 64
            for row in blocks:
                # Verify link
                if row['previous_hash'] != prev_hash:
                    return False, f"Chain broken at block {row['block_index']}"

                # Verify hash
                computed = self._compute_block_hash(
                    row['block_index'], row['timestamp'],
                    row['transactions_hash'], row['previous_hash']
                )
                if row['current_hash'] != computed:
                    return False, f"Invalid hash at block {row['block_index']}"

                prev_hash = row['current_hash']

            return True, "Chain is valid"

        finally:
            conn.close()

    def get_all_transactions(self) -> List[Transaction]:
        """
        Retrieve and decrypt all transactions from the chain.
        Returns flattened list of all transactions.
        """
        if not self._initialized:
            raise ValueError("Blockchain not unlocked")

        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blocks ORDER BY block_index")
            blocks = cursor.fetchall()

            all_transactions = []
            for row in blocks:
                block = Block(
                    index=row['block_index'],
                    timestamp=row['timestamp'],
                    transactions_hash=row['transactions_hash'],
                    encrypted_data=row['encrypted_data'],
                    nonce=row['nonce'],
                    previous_hash=row['previous_hash'],
                    current_hash=row['current_hash']
                )
                txs = self.decrypt_block_transactions(block)
                all_transactions.extend(txs)

            return all_transactions

        finally:
            conn.close()

    def get_chain_info(self) -> dict:
        """Get blockchain metadata."""
        conn = self._connect()
        try:
            cursor = conn.cursor()

            info = {
                'exists': self.db_path.exists(),
                'unlocked': self._initialized,
                'chain_length': self._chain_length,
                'genesis_hash': self._genesis_hash[:16] + '...' if self._genesis_hash else None
            }

            if self.db_path.exists():
                cursor.execute("SELECT value FROM metadata WHERE key = 'created_at'")
                row = cursor.fetchone()
                info['created_at'] = row['value'] if row else 'Unknown'

            return info

        finally:
            conn.close()

    def lock(self):
        """Lock the blockchain and clear master key from memory."""
        self.crypto.clear_key()
        self._initialized = False
