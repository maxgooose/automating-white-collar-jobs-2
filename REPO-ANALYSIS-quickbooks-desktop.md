# Repo Analysis: selfjared1/quickbooks_desktop

**Repo:** https://github.com/selfjared1/quickbooks_desktop

---

## What It Is

A **Python library** that wraps the QuickBooks Desktop SDK. It handles all the qbXML complexity for you.

Instead of writing raw XML:
```xml
<InvoiceAdd>
  <CustomerRef><FullName>SJS</FullName></CustomerRef>
  ...
</InvoiceAdd>
```

You write Python:
```python
from quickbooks_desktop import QuickbooksDesktop, Invoice

qb = QuickbooksDesktop()
qb.open_connection()
qb.begin_session()

invoice = Invoice.Add(
    customer_ref=CustomerRef(full_name="SJS"),
    template_ref=TemplateRef(full_name="INVOICE R2 FULLY FUNCTIONAL"),
    memo="PS-7310",
    invoice_line_add=[
        InvoiceLineAdd(
            item_ref=ItemRef(full_name="IPHONE 12"),
            desc="128GB-BLACK C(AMZ)",
            quantity=1,
            rate=100.00,
            serial_number="353222108267157"
        )
    ]
)

response = qb.send_xml(invoice.to_xml())
qb.close_qb()
```

---

## Is It Helpful?

**Yes. Very helpful for your use case.**

| Your Requirement | Supported |
|------------------|-----------|
| Create Invoices | Yes |
| Serial Numbers (IMEI) | Yes - `serial_number` field exists |
| Templates | Yes - `template_ref` field |
| Multiple Line Items | Yes - list of `InvoiceLineAdd` |
| Credit Memos | Yes - `credit_memos.py` exists |
| Bill Credits | Yes - `credit_card_credits.py` exists |
| Purchase Orders | Yes - `purchase_orders.py` exists |
| Item Receipts | Likely - check `transactions/` folder |

---

## Key Features

1. **Python Dataclasses** - Clean, typed objects for all QB entities
2. **Auto XML Generation** - `.to_xml()` converts Python to qbXML
3. **Auto XML Parsing** - Responses parsed back to Python objects
4. **Session Management** - Handles open/close connection automatically
5. **Supports Enterprise** - Uses same SDK that works with all Desktop versions

---

## Supported Transactions

From `/src/quickbooks_desktop/transactions/`:
- invoices.py
- credit_memos.py
- bills.py
- purchase_orders.py
- sales_orders.py
- estimates.py
- deposits.py
- checks.py
- receive_payments.py
- journal_entries.py
- inventory_adjustments.py
- and more

---

## Requirements

| Requirement | Details |
|-------------|---------|
| OS | Windows only |
| Python | 32-bit for QB before 2022, 64-bit for QB 2022+ |
| QuickBooks | Must be open with company file loaded |
| Dependencies | win32com, lxml |

---

## Serial Number Support

From `invoices.py`, the `InvoiceLineAdd` class has:

```python
serial_number: Optional[str] = field(
    default=None,
    metadata={
        "name": "SerialNumber",
        "type": "Element",
        "max_length": 4095,
    },
)
```

This means you can add IMEI numbers directly to invoice lines.

---

## How It Connects

Uses `win32com.client` to talk to QuickBooks:

```python
self.dispatch_str = "QBXMLRP2.RequestProcessor"
self.qbXMLRP = win32com.client.Dispatch(self.dispatch_str)
self.qbXMLRP.OpenConnection2('', self.application_name, 1)
self.ticket = self.qbXMLRP.BeginSession("", 0)
```

Same underlying mechanism as SDKTestPlus3 - just wrapped in Python.

---

## Pros

- Eliminates need to write raw qbXML
- Python is easier than C#/VB.NET for quick development
- Well-structured with dataclasses
- Supports serial numbers out of the box
- Free and open source
- Active development (check commit history)

---

## Cons

- Windows only (Python + QuickBooks)
- Must use 32-bit Python for older QB versions
- QuickBooks must be running
- Less documentation than official SDK
- Fewer stars/community support than commercial tools

---

## Verdict

**Recommended to try.**

This library could significantly speed up development. Instead of learning qbXML from scratch, you use Python objects.

---

## Next Steps If Using This

1. Clone the repo
2. Install on Windows machine with QuickBooks
3. Install dependencies: `pip install win32com lxml`
4. Open QuickBooks with company file
5. Test connection:
```python
from quickbooks_desktop import QuickbooksDesktop
qb = QuickbooksDesktop()
qb.open_connection()
qb.begin_session()
print("Connected!")
qb.close_qb()
```
6. If that works, test a simple invoice query
7. Then test invoice creation

---

## Alternative Consideration

If you hit issues with this library, the fallback is:
- Use the same approach but write your own qbXML
- Or use Conductor (REST API) if budget allows

---

## Links

- Repo: https://github.com/selfjared1/quickbooks_desktop
- QuickBooks XML Reference: https://static.developer.intuit.com/qbSDK-current/common/newosr/index.html
