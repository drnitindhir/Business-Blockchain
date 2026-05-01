"""
Command-line interface for Business Blockchain.
Secure, encrypted transaction recording system.
"""

import sys
import getpass
import json
from datetime import datetime

from blockchain import Blockchain
from transaction import Transaction, create_transaction


DEFAULT_DB_PATH = "business_chain.db"


def get_password(prompt: str = "Enter master password: ", confirm: bool = False) -> str:
    """Securely get password from user."""
    password = getpass.getpass(prompt)
    if confirm:
        password2 = getpass.getpass("Confirm master password: ")
        if password != password2:
            print("ERROR: Passwords do not match!")
            sys.exit(1)
    return password


def print_block(block, crypto_manager=None):
    """Print block information."""
    print(f"\n{'='*60}")
    print(f"BLOCK #{block.index}")
    print(f"{'='*60}")
    print(f"  Timestamp:      {block.timestamp}")
    print(f"  Hash:           {block.current_hash[:32]}...")
    print(f"  Previous Hash:  {block.previous_hash[:32] if block.previous_hash != '0'*64 else 'GENESIS'}...")
    print(f"  TX Hash:        {block.transactions_hash[:32]}...")


def print_transaction(tx, index=None):
    """Print transaction details."""
    prefix = f"[{index}] " if index is not None else ""
    print(f"  {prefix}{tx.transaction_type.upper()} - ${tx.amount:.2f} {tx.currency}")
    if tx.description:
        print(f"      Description: {tx.description}")
    if tx.from_account:
        print(f"      From: {tx.from_account}")
    if tx.to_account:
        print(f"      To: {tx.to_account}")
    if tx.reference_id:
        print(f"      Reference: {tx.reference_id}")
    print(f"      Time: {tx.timestamp}")


def cmd_init(args):
    """Initialize a new blockchain."""
    db_path = args.db if args.db else DEFAULT_DB_PATH

    print(f"Initializing new blockchain at: {db_path}")
    print("WARNING: Store your master password securely!")
    print("         Without it, your data is permanently encrypted.\n")

    password = get_password(confirm=True)

    chain = Blockchain(db_path)
    if chain.initialize_chain(password):
        print("\n[SUCCESS] Blockchain initialized!")
        print(f"  Genesis hash: {chain._genesis_hash[:48]}...")
        print("\nRemember: Your transactions are encrypted with AES-256-GCM")
        print("          Only someone with the master password can decrypt them")
    else:
        print("\n[ERROR] Blockchain already exists at this location!")
        print("        Use a different path or unlock existing chain.")


def cmd_unlock(args):
    """Unlock existing blockchain."""
    db_path = args.db if args.db else DEFAULT_DB_PATH

    chain = Blockchain(db_path)
    if not chain.db_path.exists():
        print(f"[ERROR] Blockchain not found at: {db_path}")
        print("        Use 'init' to create a new blockchain.")
        return

    password = get_password()
    success, message = chain.unlock(password)

    if success:
        print(f"\n[SUCCESS] {message}")
        info = chain.get_chain_info()
        print(f"  Chain length: {info['chain_length']} blocks")
        print(f"  Created: {info['created_at']}")
    else:
        print(f"\n[ERROR] {message}")
        sys.exit(1)

    return chain


def cmd_lock(args, chain):
    """Lock blockchain and clear key from memory."""
    chain.lock()
    print("[SUCCESS] Blockchain locked. Master key cleared from memory.")


def cmd_add(args, chain):
    """Add a new transaction."""
    print("\n--- New Transaction ---")

    # Get transaction details
    tx_type = args.type if args.type else input(
        "Type (payment/invoice/expense/transfer/refund/adjustment): "
    ).strip().lower()

    try:
        amount = float(args.amount) if args.amount else float(
            input("Amount: ")
        )
    except ValueError:
        print("[ERROR] Invalid amount!")
        return

    currency = args.currency if args.currency else input("Currency [USD]: ").strip() or "USD"
    description = args.description if args.description else input("Description: ").strip()
    from_account = args.from_account if args.from_account else input("From Account: ").strip()
    to_account = args.to_account if args.to_account else input("To Account: ").strip()
    reference_id = args.reference if args.reference else input("Reference ID: ").strip()

    tx = create_transaction(
        transaction_type=tx_type,
        amount=amount,
        currency=currency,
        description=description,
        from_account=from_account,
        to_account=to_account,
        reference_id=reference_id
    )

    # Validate
    is_valid, error = tx.validate()
    if not is_valid:
        print(f"[ERROR] {error}")
        return

    # Add to chain
    block = chain.add_transactions([tx])
    print(f"\n[SUCCESS] Transaction added in Block #{block.index}")
    print(f"  Block hash: {block.current_hash[:48]}...")


def cmd_view(args, chain):
    """View blocks and transactions."""
    if args.block is not None:
        # View specific block
        block = chain.get_block(args.block)
        if not block:
            print(f"[ERROR] Block #{args.block} not found")
            return

        print_block(block)

        if args.decrypt:
            try:
                txs = chain.decrypt_block_transactions(block)
                print(f"\n  Transactions ({len(txs)}):")
                for i, tx in enumerate(txs):
                    print_transaction(tx, i + 1)
            except Exception as e:
                print(f"\n[ERROR] Could not decrypt: {e}")
    else:
        # View all transactions
        try:
            txs = chain.get_all_transactions()
            print(f"\n--- All Transactions ({len(txs)}) ---")
            for i, tx in enumerate(txs):
                print_transaction(tx, i + 1)
        except Exception as e:
            print(f"[ERROR] {e}")


def cmd_status(args, chain):
    """Show blockchain status."""
    info = chain.get_chain_info()
    print("\n--- Blockchain Status ---")
    print(f"  Database:     {chain.db_path}")
    print(f"  Unlocked:     {info['unlocked']}")
    print(f"  Chain Length: {info['chain_length']} blocks")
    print(f"  Created:      {info['created_at']}")
    print(f"  Genesis Hash: {info['genesis_hash']}")

    if info['unlocked']:
        valid, msg = chain.verify_chain()
        print(f"  Chain Valid:  {valid}")
        if not valid:
            print(f"  Error: {msg}")


def cmd_verify(args, chain):
    """Verify chain integrity."""
    print("Verifying blockchain integrity...")
    valid, msg = chain.verify_chain()
    if valid:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")
        sys.exit(1)


def cmd_export(args, chain):
    """Export transactions to JSON file."""
    try:
        txs = chain.get_all_transactions()
        output = args.output if args.output else "transactions_export.json"

        data = {
            'exported_at': datetime.utcnow().isoformat(),
            'transaction_count': len(txs),
            'transactions': [tx.to_dict() for tx in txs]
        }

        with open(output, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n[SUCCESS] Exported {len(txs)} transactions to: {output}")
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")


def cmd_import(args, chain):
    """Import transactions from JSON file."""
    input_file = args.input

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)

        tx_dicts = data.get('transactions', [data])
        transactions = [Transaction.from_dict(tx) for tx in tx_dicts]

        print(f"Importing {len(transactions)} transactions...")
        block = chain.add_transactions(transactions)
        print(f"[SUCCESS] Imported to Block #{block.index}")

    except Exception as e:
        print(f"[ERROR] Import failed: {e}")


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Business Blockchain - Encrypted Transaction Ledger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init                    # Create new blockchain
  %(prog)s unlock                  # Unlock with master password
  %(prog)s add --type payment --amount 1000 --to "Vendor ABC"
  %(prog)s view --decrypt          # View all transactions (decrypted)
  %(prog)s status                  # Show chain status
  %(prog)s verify                  # Verify chain integrity
        """
    )

    parser.add_argument('--db', '-d', help='Database path (default: business_chain.db)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Init command
    subparsers.add_parser('init', help='Initialize new blockchain')

    # Unlock command
    subparsers.add_parser('unlock', help='Unlock blockchain')

    # Add transaction command
    add_parser = subparsers.add_parser('add', help='Add transaction')
    add_parser.add_argument('--type', '-t', help='Transaction type')
    add_parser.add_argument('--amount', '-a', help='Amount')
    add_parser.add_argument('--currency', '-c', default='USD', help='Currency')
    add_parser.add_argument('--description', '-desc', help='Description')
    add_parser.add_argument('--from', dest='from_account', help='From account')
    add_parser.add_argument('--to', dest='to_account', help='To account')
    add_parser.add_argument('--reference', '-r', help='Reference ID')

    # View command
    view_parser = subparsers.add_parser('view', help='View transactions')
    view_parser.add_argument('--block', '-b', type=int, help='Specific block number')
    view_parser.add_argument('--decrypt', action='store_true', help='Decrypt transactions')

    # Status command
    subparsers.add_parser('status', help='Show blockchain status')

    # Verify command
    subparsers.add_parser('verify', help='Verify chain integrity')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export transactions')
    export_parser.add_argument('--output', '-o', help='Output file')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import transactions')
    import_parser.add_argument('--input', '-i', required=True, help='Input file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Commands that don't need unlock
    if args.command == 'init':
        cmd_init(args)
        return

    # All other commands need unlock
    chain = Blockchain(args.db if args.db else DEFAULT_DB_PATH)

    if args.command == 'unlock':
        cmd_unlock(args)
    elif args.command == 'add':
        if not chain._initialized:
            password = get_password()
            success, msg = chain.unlock(password)
            if not success:
                print(f"[ERROR] {msg}")
                sys.exit(1)
        cmd_add(args, chain)
    elif args.command == 'view':
        if not chain._initialized:
            password = get_password()
            success, msg = chain.unlock(password)
            if not success:
                print(f"[ERROR] {msg}")
                sys.exit(1)
        cmd_view(args, chain)
    elif args.command == 'status':
        if not chain._initialized:
            password = get_password()
            success, msg = chain.unlock(password)
            if not success:
                print(f"[ERROR] {msg}")
                sys.exit(1)
        cmd_status(args, chain)
    elif args.command == 'verify':
        if not chain._initialized:
            password = get_password()
            success, msg = chain.unlock(password)
            if not success:
                print(f"[ERROR] {msg}")
                sys.exit(1)
        cmd_verify(args, chain)
    elif args.command == 'export':
        if not chain._initialized:
            password = get_password()
            success, msg = chain.unlock(password)
            if not success:
                print(f"[ERROR] {msg}")
                sys.exit(1)
        cmd_export(args, chain)
    elif args.command == 'import':
        if not chain._initialized:
            password = get_password()
            success, msg = chain.unlock(password)
            if not success:
                print(f"[ERROR] {msg}")
                sys.exit(1)
        cmd_import(args, chain)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
