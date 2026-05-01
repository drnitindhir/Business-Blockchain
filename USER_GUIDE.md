# Business Blockchain - User Guide

## Getting Started

### First Time Setup

1. **Run the setup** (one time only):
   - Double-click `SETUP.bat`
   - Wait for installation to complete
   - Tests will run automatically

2. **Start the application**:
   - Double-click `QUICK_START.bat` for menu-driven interface
   - Or double-click `run.bat` and type commands manually

---

## Common Tasks

### 1. Create Your First Blockchain

```
Option 1 from menu, or type: run.bat init
```

You will be asked to enter a **Master Password**.

**IMPORTANT:** 
- Use a strong password (12+ characters)
- Write it down and store it safely
- **Without this password, your data is permanently encrypted**

---

### 2. Add a Transaction

```
Option 2 from menu, or type: run.bat add
```

You'll be prompted for:
- **Type**: payment, invoice, expense, transfer, refund, or adjustment
- **Amount**: e.g., 1500.50
- **Currency**: e.g., USD (default)
- **Description**: What is this for?
- **From Account**: Your account name
- **To Account**: Recipient name
- **Reference ID**: Invoice number, receipt #, etc.

**Example:**
```
Type: payment
Amount: 2500
Description: Office equipment purchase
From: Business Checking
To: ABC Electronics
Reference: INV-2026-001
```

---

### 3. View Your Transactions

```
Option 3 from menu, or type: run.bat view --decrypt
```

Enter your master password to see all transactions.

**To view a specific block:**
```
run.bat view --block 1 --decrypt
```

---

### 4. Check Status

```
Option 4 from menu, or type: run.bat status
```

Shows:
- Number of blocks
- Creation date
- Whether chain is valid

---

### 5. Verify Integrity

```
Option 5 from menu, or type: run.bat verify
```

Confirms that no one has tampered with your blockchain.

---

### 6. Export Data

```
Option 6 from menu, or type: run.bat export
```

Creates a JSON file with all transactions (for backup or accounting software).

**WARNING:** Exported files are NOT encrypted!

---

## Command Reference

| Command | What It Does |
|---------|--------------|
| `init` | Create new blockchain |
| `add` | Add a transaction |
| `view --decrypt` | See all transactions |
| `view --block 1 --decrypt` | See specific block |
| `status` | Show blockchain info |
| `verify` | Check for tampering |
| `export -o file.json` | Save to file |
| `import -i file.json` | Load from file |

---

## Security Best Practices

### Do:
- Use a strong, unique master password
- Back up the `business_chain.db` file regularly
- Store backups on encrypted USB or secure cloud storage
- Lock your computer when away
- Keep Windows and antivirus updated

### Don't:
- Share your master password
- Store password in plain text on the same PC
- Email unencrypted transaction exports
- Run this on shared/public computers

---

## Backup Your Data

Your blockchain is stored in: `business_chain.db`

**To backup:**
1. Copy `business_chain.db` to USB drive or cloud storage
2. Keep your master password separate from the backup

**To restore:**
1. Place `business_chain.db` in the BusinessBlockchain folder
2. Use your master password to unlock

---

## Troubleshooting

### "Blockchain not found"
Run `init` to create a new blockchain.

### "Invalid master password"
Double-check your password. It's case-sensitive.

### "Chain is invalid"
This could mean:
- Database file corruption
- Tampering attempt
- Contact technical support immediately

### Application won't start
1. Make sure Python is installed
2. Re-run `SETUP.bat`
3. Check Windows Defender hasn't blocked the scripts

---

## File Locations

```
C:\Users\DELL\BusinessBlockchain\
├── SETUP.bat          ← Run this first
├── QUICK_START.bat    ← Easy menu interface
├── run.bat            ← Direct command access
├── business_chain.db  ← Your encrypted blockchain
├── venv/              ← Python environment (auto-created)
└── *.py               ← Application code
```

---

## Need Help?

Run with `--help` for command details:
```
run.bat --help
run.bat add --help
```

---

## Transaction Types Explained

| Type | When to Use |
|------|-------------|
| `payment` | Money going out to vendors/suppliers |
| `invoice` | Money received from customers |
| `expense` | Business expenses (meals, travel, etc.) |
| `transfer` | Moving money between your accounts |
| `refund` | Refunds issued or received |
| `adjustment` | Accounting corrections |

---

**Version:** 1.0  
**Last Updated:** 2026-04-30
