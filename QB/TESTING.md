# QuickBooks Connection Testing Guide

This document explains how to test the QuickBooks Desktop connection using the diagnostics page.

## Prerequisites

Before testing, ensure you have:

1. **Windows machine** - QuickBooks Desktop SDK only works on Windows
2. **QuickBooks Desktop Enterprise** installed and running
3. **Company file open** - QuickBooks must have a company file loaded
4. **Python dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

## Starting the Server

1. Open a terminal in the `QB` directory
2. Run the Flask server:
   ```bash
   python app.py
   ```
3. Server starts at `http://localhost:5000`

## Accessing the Diagnostics Page

Navigate to: **http://localhost:5000/diagnostics**

You'll see a dashboard with 5 test buttons:

| Button | Purpose |
|--------|---------|
| **Test Connection** | Verifies QB SDK is accessible |
| **Query Customers** | Tests read access - lists customers |
| **Query Invoices** | Tests read access - lists invoices |
| **Create Test Invoice** | Tests write access - creates a test invoice |
| **Setup Sample Data** | Creates test customer and items |

## Recommended Testing Flow

### Step 1: Test Connection
Click **Test Connection** first. Expected output:
```
✓ Connection opened
✓ Session started
✓ Connection closed

✅ QuickBooks connection successful!
```

If this fails, check:
- Is QuickBooks running?
- Is a company file open?
- Has the app been authorized in QuickBooks?

### Step 2: Setup Sample Data
Click **Setup Sample Data** to create test data. Expected output:
```
✓ Connected to QuickBooks
✓ Session started

Creating customer...
  ✓ Created customer: Universal Cellular Customer

Creating sample items...
  ✓ Created: APPLE-IPHONE XS-A1920
  ✓ Created: APPLE-IPHONE 12
  ✓ Created: SAMSUNG-GALAXY S21
  ✓ Created: TEST-DEVICE

Summary: 4 created, 0 already existed, 0 failed

✅ Sample data setup complete
```

If items already exist, you'll see:
```
  ○ Already exists: APPLE-IPHONE XS-A1920
```

### Step 3: Query Customers
Verify the customer was created:
```
✅ Found 10 customer(s)

Customers found:
  1. Universal Cellular Customer
  2. ...
```

### Step 4: Create Test Invoice
Create a test invoice to verify write access:
```
✓ Connected
✓ Session started

Finding customer...
  Using customer: Universal Cellular Customer

Finding item...
  Using item: TEST-DEVICE

Creating invoice...
  ✓ Invoice #12345 created!
  TxnID: TXN-123456

✅ Test invoice #12345 created successfully!
```

### Step 5: Query Invoices
Verify the invoice appears:
```
✅ Found 10 invoice(s)

Recent invoices:
  #12345 - 2026-01-09 (TxnID: TXN-123456...)
```

## Testing Real Invoice Generation

After diagnostics pass, test the full workflow:

1. Go to the main page: **http://localhost:5000**
2. Upload a Receiving Report Excel file
3. Click **Generate Invoice**

### Using Real QuickBooks (not mock)

By default, the app uses mock invoice generation. To use real QuickBooks:

**Windows (Command Prompt):**
```cmd
set USE_REAL_QB=true
python app.py
```

**Windows (PowerShell):**
```powershell
$env:USE_REAL_QB="true"
python app.py
```

**Linux/Mac (development only - won't connect to QB):**
```bash
export USE_REAL_QB=true
python app.py
```

## Common Error Messages

### "Failed to connect to QuickBooks: ... Is QuickBooks running?"
- QuickBooks Desktop is not running
- Solution: Open QuickBooks and load a company file

### "Failed to begin session: ... Is a company file open?"
- QuickBooks is running but no company file is loaded
- Solution: Open a company file (File > Open or Restore Company)

### "Import Error: No module named 'win32com'"
- pywin32 is not installed
- Solution: `pip install pywin32`

### "Import Error: ... Make sure you're running on Windows"
- You're trying to run QB operations on macOS/Linux
- Solution: Use Windows for QB integration; macOS/Linux work in mock mode only

### "QuickBooks error (3100): Customer not found"
- The customer name doesn't exist in QuickBooks
- Solution: Run "Setup Sample Data" or create the customer in QB

### "QuickBooks error (3100): Item not found"
- The item/part number doesn't exist in QuickBooks
- Solution: Create the item in QB or run "Setup Sample Data"

## First-Time Authorization

The first time you connect, QuickBooks will show an authorization dialog:

1. QuickBooks prompts: "An application is trying to access QuickBooks"
2. Select **"Yes, always allow access"**
3. Check **"Allow this application to access personal data"** if needed
4. Click **Continue**

To manage authorized apps later:
- QuickBooks > Edit > Preferences > Integrated Applications > Company Preferences

## File Structure

```
QB/
├── app.py                  # Flask server with test routes
├── diagnostics.html        # Test dashboard UI
├── excel_parser.py         # Excel file parser
├── invoice_generator.py    # Mock invoice generator
├── invoice_generator_qb.py # Real QB invoice generator
├── requirements.txt        # Python dependencies
└── TESTING.md             # This file

quickbooks_desktop/
├── __init__.py            # Package marker
├── session_manager.py     # QB SDK connection wrapper
└── qb_helpers.py          # High-level QB operations
```

## Troubleshooting

### Connection works but queries fail
- Check QuickBooks user permissions
- Ensure the company file has data

### Tests pass but real invoice fails
- Verify customer name exists exactly as specified
- Verify item/part numbers exist in QuickBooks Items list
- Check the Excel file format matches expected columns

### Server crashes on Windows
- Ensure you're using the correct Python architecture (32-bit for QB pre-2022, 64-bit for QB 2022+)
- Try running as Administrator

## Support

For additional help:
1. Check the console output for detailed error messages
2. Review QuickBooks > Edit > Preferences > Integrated Applications for app status
3. Check Windows Event Viewer for COM errors
