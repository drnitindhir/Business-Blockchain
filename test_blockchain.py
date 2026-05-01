"""
Test suite for Business Blockchain.
Run with: python test_blockchain.py
"""

import os
import sys
from blockchain import Blockchain
from transaction import create_transaction

DB_PATH = "test_blockchain.db"
PASSWORD = "TestMasterPassword123!"


def cleanup():
    """Remove test database if exists."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_initialization():
    """Test blockchain initialization."""
    print("\n=== Test: Blockchain Initialization ===")
    chain = Blockchain(DB_PATH)

    result = chain.initialize_chain(PASSWORD)
    assert result, "Initialization should succeed"
    assert chain.db_path.exists(), "Database file should exist"
    assert len(chain._genesis_hash) == 64, "Genesis hash should be 64 chars"

    print("[PASS] Blockchain initialized correctly")
    return chain


def test_add_transactions(chain):
    """Test adding transactions."""
    print("\n=== Test: Add Transactions ===")

    tx1 = create_transaction(
        transaction_type='payment',
        amount=1500.00,
        description='Office supplies',
        from_account='Checking',
        to_account='ABC Supplies',
        reference_id='INV-001'
    )

    tx2 = create_transaction(
        transaction_type='invoice',
        amount=5000.00,
        description='Client payment',
        from_account='Client XYZ',
        to_account='Checking',
        reference_id='PAY-001'
    )

    block = chain.add_transactions([tx1, tx2])
    assert block.index == 1, "Should be block #1"

    print(f"[PASS] Added 2 transactions in Block #{block.index}")
    return block


def test_decryption(chain, block):
    """Test transaction decryption."""
    print("\n=== Test: Decryption ===")

    txs = chain.decrypt_block_transactions(block)
    assert len(txs) == 2, "Should have 2 transactions"
    assert txs[0].transaction_type == 'payment', "First TX should be payment"
    assert txs[1].amount == 5000.00, "Second TX amount should match"

    print(f"[PASS] Decrypted {len(txs)} transactions correctly")


def test_chain_verification(chain):
    """Test chain integrity verification."""
    print("\n=== Test: Chain Verification ===")

    valid, msg = chain.verify_chain()
    assert valid, f"Chain should be valid: {msg}"

    print(f"[PASS] {msg}")


def test_password_security():
    """Test password verification."""
    print("\n=== Test: Password Security ===")

    # Wrong password should fail
    chain2 = Blockchain(DB_PATH)
    success, msg = chain2.unlock("WrongPassword")
    assert not success, "Wrong password should fail"
    assert "Invalid" in msg, "Should show invalid message"

    # Correct password should succeed
    success, msg = chain2.unlock(PASSWORD)
    assert success, f"Correct password should work: {msg}"

    print("[PASS] Password security works correctly")


def test_lock_unlock():
    """Test lock functionality."""
    print("\n=== Test: Lock/Unlock ===")

    chain3 = Blockchain(DB_PATH)
    chain3.unlock(PASSWORD)

    # Should work when unlocked
    txs = chain3.get_all_transactions()
    assert len(txs) > 0, "Should have transactions"

    # Lock
    chain3.lock()

    # Should fail when locked
    try:
        chain3.get_all_transactions()
        assert False, "Should raise error when locked"
    except ValueError:
        print("[PASS] Lock clears key from memory")


def test_multiple_blocks():
    """Test multiple blocks in chain."""
    print("\n=== Test: Multiple Blocks ===")

    chain4 = Blockchain(DB_PATH)
    chain4.unlock(PASSWORD)

    # Add more blocks
    for i in range(3):
        tx = create_transaction(
            transaction_type='expense',
            amount=100 + i * 50,
            description=f'Expense #{i+1}',
            from_account='Checking',
            to_account=f'Vendor {i+1}'
        )
        block = chain4.add_transactions([tx])
        assert block.index == 2 + i, f"Should be block #{2+i}"

    # Verify chain
    valid, msg = chain4.verify_chain()
    assert valid, f"Chain should still be valid: {msg}"

    print(f"[PASS] Multiple blocks added, chain valid")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Business Blockchain Test Suite")
    print("=" * 50)

    cleanup()

    try:
        chain = test_initialization()
        block = test_add_transactions(chain)
        test_decryption(chain, block)
        test_chain_verification(chain)
        test_password_security()
        test_lock_unlock()
        test_multiple_blocks()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    finally:
        cleanup()
        print("\nTest database cleaned up.")


if __name__ == "__main__":
    main()
