# Business Blockchain - Encrypted Transaction Ledger

A private, master-key-based blockchain system for recording business transactions with military-grade encryption.

## Security Features

- **AES-256-GCM Encryption**: All transaction data encrypted with authenticated encryption
- **Argon2id Key Derivation**: Password hardened against GPU/ASIC attacks (64MB memory, 3 iterations)
- **Single Master Key**: Only the master password holder can decrypt transactions
- **Local Storage**: SQLite database stored on single PC - no network exposure
- **Chain Integrity**: SHA-256 hashes link blocks - tampering is detectable

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Master Password                          │
│                          │                                  │
│                          ▼                                  │
│                    Argon2id KDF                             │
│                          │                                  │
│                          ▼                                  │
│                    AES-256 Key                              │
│                          │                                  │
│         ┌────────────────┼────────────────┐                │
│         ▼                ▼                ▼                │
│    ┌─────────┐     ┌─────────┐     ┌─────────┐            │
│    │ Block 0 │────▶│ Block 1 │────▶│ Block 2 │            │
│    │(Genesis)│     │(Enc TXs)│     │(Enc TXs)│            │
│    └─────────┘     └─────────┘     └─────────┘            │
│         │               │               │                  │
│         ▼               ▼               ▼                  │
│    SHA-256 hash    SHA-256 hash    SHA-256 hash           │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd BusinessBlockchain
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize a new blockchain

```bash
python cli.py init
```

You'll be prompted to set a master password. **Store this securely** - without it, your data is permanently encrypted.

### 2. Unlock the blockchain

```bash
python cli.py unlock
```

### 3. Add transactions

```bash
# Interactive mode
python cli.py add

# Or with arguments
python cli.py add --type payment --amount 1500 --to "ABC Supplies" --desc "Office supplies"
```

### 4. View transactions

```bash
# View all (decrypted)
python cli.py view --decrypt

# View specific block
python cli.py view --block 1 --decrypt
```

### 5. Verify chain integrity

```bash
python cli.py verify
```

### 6. Export transactions

```bash
python cli.py export --output my_transactions.json
```

## Transaction Types

- `payment` - Outgoing payments
- `invoice` - Received invoices
- `expense` - Business expenses
- `transfer` - Account transfers
- `refund` - Refunds issued/received
- `adjustment` - Accounting adjustments

## Command Reference

| Command | Description |
|---------|-------------|
| `init` | Create new blockchain |
| `unlock` | Unlock with master password |
| `add` | Add transaction(s) |
| `view` | View blocks/transactions |
| `status` | Show chain info |
| `verify` | Verify integrity |
| `export` | Export to JSON |
| `import` | Import from JSON |

## Security Best Practices

1. **Master Password**: Use a strong, unique password (16+ characters)
2. **Backup**: Regularly backup the `.db` file to secure location
3. **Memory**: Key is cleared from memory when locked/exits
4. **No Network**: Keep database on offline/isolated PC for maximum security
5. **Export Carefully**: Exported JSON is NOT encrypted

## File Structure

```
BusinessBlockchain/
├── cli.py              # Command-line interface
├── blockchain.py       # Core blockchain logic
├── transaction.py      # Transaction definitions
├── crypto_core.py      # Encryption/key derivation
├── requirements.txt    # Python dependencies
└── business_chain.db   # Encrypted blockchain (created on init)
```

## Technical Details

### Encryption Scheme
- **Key Derivation**: Argon2id (64MB, 3 iterations, 4 threads)
- **Block Encryption**: AES-256-GCM with 96-bit nonce
- **Hashing**: SHA-256 for block links and transaction hashes

### Block Structure
```python
Block {
    index: int              # Block number
    timestamp: str          # ISO timestamp
    transactions_hash: str  # SHA-256 of TX data
    encrypted_data: str     # Base64(AES-GCM ciphertext)
    nonce: str              # Base64(12-byte nonce)
    previous_hash: str      # SHA-256 of previous block
    current_hash: str       # SHA-256 of header
}
```

### Storage
- SQLite database with encrypted BLOBs
- Only block headers visible without key
- Master key never stored - derived from password each session

## License

MIT License - Use at your own risk for business purposes.
