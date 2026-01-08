# QuickBooks Enterprise Integration Options — Deep Research

> **Purpose:** Document all available integration options for automating packing slip → invoice creation in QuickBooks Enterprise Desktop. An agent or human will use this to make the final decision.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Option 1: QuickBooks SDK (QBSDK)](#option-1-quickbooks-sdk-qbsdk)
3. [Option 2: QuickBooks Web Connector (QBWC)](#option-2-quickbooks-web-connector-qbwc)
4. [Option 3: Conductor](#option-3-conductor)
5. [Option 4: Transaction Pro](#option-4-transaction-pro)
6. [Option 5: SaaSAnt](#option-5-saasant)
7. [Option 6: Coefficient](#option-6-coefficient)
8. [Option 7: Apix Drive](#option-7-apix-drive)
9. [Option 8: FinJinni](#option-8-finjinni)
10. [Option 9: DBSync](#option-9-dbsync)
11. [Option 10: Python Library (selfjared1/quickbooks_desktop)](#option-10-python-library)
12. [Comparison Matrix](#comparison-matrix)
13. [Decision Criteria](#decision-criteria)
14. [Open Questions](#open-questions)

---

## Executive Summary

| Approach | Best For | Enterprise Support | Automation Level | Cost |
|----------|----------|-------------------|------------------|------|
| QBSDK | Full control, no dependencies | ✅ | Full | Free |
| QBWC | Web-based automation | ✅ | Full | Free |
| Conductor | Modern REST API | ✅ | Full | ~$50-100/mo |
| Transaction Pro | No-code imports | ✅ | Semi-manual | ~$200-400 |
| SaaSAnt | Excel power users | ✅ | Semi-manual | ~$30-50/mo |
| Coefficient | Spreadsheet-first | ⚠️ Verify | Semi-manual | Free tier available |
| Apix Drive | iPaaS workflows | ⚠️ Verify | Full | ~$20-50/mo |
| FinJinni | Financial automation | ⚠️ Verify | Full | Contact sales |
| DBSync | Enterprise sync | ✅ | Full | ~$50-200/mo |
| Python Library | Python devs, free SDK wrapper | ✅ | Full | Free |

---

## Option 1: QuickBooks SDK (QBSDK)

### Overview
The official Software Development Kit from Intuit for integrating with QuickBooks Desktop products.

### Technical Details
- **Communication:** qbXML (XML-based request/response)
- **Connection:** Local COM/DLL calls or via Web Connector
- **Languages:** C#, VB.NET, C++, Node.js (via COM wrappers)
- **Authentication:** Application certificate + user authorization in QB

### Requirements
- QuickBooks Desktop must be installed
- QuickBooks must be running during operations
- Windows environment (SDK is Windows-only)
- Application must be registered with QuickBooks

### Capabilities
| Feature | Supported |
|---------|-----------|
| Create Invoices | ✅ Yes |
| Create Credit Memos | ✅ Yes |
| Create Bill Credits | ✅ Yes |
| Create Item Receipts | ✅ Yes |
| Create Purchase Orders | ✅ Yes |
| Read/Query Data | ✅ Yes |
| Custom Fields | ✅ Yes |
| Serial Numbers | ✅ Yes |
| Use Templates | ✅ Yes |
| Batch Operations | ✅ Yes (loop) |

### Sample qbXML for Invoice Creation
```xml
<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>SJS</FullName>
        </CustomerRef>
        <TemplateRef>
          <FullName>INVOICE R2 FULLY FUNCTIONAL</FullName>
        </TemplateRef>
        <TxnDate>2026-01-05</TxnDate>
        <Memo>PS-7310</Memo>
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>IPHONE 12</FullName>
          </ItemRef>
          <Desc>128GB-BLACK C(AMZ)</Desc>
          <Quantity>1</Quantity>
          <Rate>100.00</Rate>
          <SerialNumber>353222108267157</SerialNumber>
        </InvoiceLineAdd>
      </InvoiceAdd>
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>
```

### Pros
- ✅ **Free** — no licensing costs
- ✅ **Full control** — access to all QB features
- ✅ **No third-party dependency** — direct to QB
- ✅ **Works offline** — no internet required
- ✅ **Enterprise supported** — full compatibility

### Cons
- ❌ **Complex XML** — qbXML has steep learning curve
- ❌ **Windows only** — SDK requires Windows
- ❌ **QB must be running** — can't operate headlessly easily
- ❌ **Local only** — must run on same machine/network as QB
- ❌ **Development time** — requires significant coding

### Cost
- **Free** (SDK download from Intuit)

### Links
- Developer Portal: https://developer.intuit.com/
- SDK Download: Available after developer registration
- qbXML Reference: Included in SDK

---

## Option 2: QuickBooks Web Connector (QBWC)

### Overview
A middleware application from Intuit that allows web-based applications to communicate with QuickBooks Desktop.

### Technical Details
- **Communication:** SOAP/XML over HTTPS
- **Architecture:** Web service ↔ Web Connector ↔ QuickBooks
- **Languages:** Any (builds a web service endpoint)
- **Sync:** Scheduled intervals or manual trigger

### How It Works
```
┌─────────────────┐     HTTPS/SOAP     ┌──────────────────┐     qbXML     ┌─────────────┐
│   Your Web      │ ←───────────────→  │   QuickBooks     │ ←──────────→  │  QuickBooks │
│   Application   │                    │   Web Connector  │               │  Enterprise │
└─────────────────┘                    └──────────────────┘               └─────────────┘
```

### Requirements
- QuickBooks Desktop installed
- QuickBooks Web Connector installed (free download)
- Web service endpoint (your code)
- .qwc file to register your service

### Capabilities
Same as QBSDK — full access to all QuickBooks features.

### SOAP Methods Required
| Method | Purpose |
|--------|---------|
| `serverVersion` | Return your app version |
| `clientVersion` | Check client compatibility |
| `authenticate` | Validate credentials |
| `sendRequestXML` | Send qbXML request to QB |
| `receiveResponseXML` | Receive QB response |
| `getLastError` | Error handling |
| `closeConnection` | End session |

### Pros
- ✅ **Free** — no cost for Web Connector
- ✅ **Web-based** — can run from any server
- ✅ **Scheduled automation** — set intervals
- ✅ **QB doesn't need to be constantly open** — opens during sync
- ✅ **Enterprise supported** — full compatibility
- ✅ **Multi-user friendly** — works in multi-user mode

### Cons
- ❌ **Not real-time** — scheduled sync only
- ❌ **SOAP complexity** — must implement SOAP web service
- ❌ **Still uses qbXML** — same XML complexity as SDK
- ❌ **Debugging difficult** — multiple layers
- ❌ **Windows required** — for the Web Connector

### Cost
- **Free**

### Links
- Web Connector Download: https://developer.intuit.com/app/developer/qbdesktop/docs/get-started/get-started-with-quickbooks-web-connector
- Documentation: Included in QB SDK

---

## Option 3: Conductor

### Overview
A third-party REST API wrapper that sits between your application and QuickBooks Desktop, translating modern REST calls into qbXML.

### Technical Details
- **Communication:** REST API (JSON)
- **Architecture:** Your App → Conductor Cloud → Conductor Agent → QuickBooks
- **Languages:** Any (standard REST)
- **Sync:** Real-time (via local agent)

### How It Works
```
┌─────────────────┐      REST/JSON      ┌─────────────────┐     qbXML     ┌─────────────┐
│   Your App      │ ←────────────────→  │   Conductor     │ ←──────────→  │  QuickBooks │
│   (any lang)    │                     │   Agent         │               │  Enterprise │
└─────────────────┘                     └─────────────────┘               └─────────────┘
```

### Requirements
- Conductor account
- Conductor desktop agent installed
- QuickBooks Desktop running
- Internet connection

### API Example
```javascript
// Create Invoice via Conductor REST API
const response = await fetch('https://api.conductor.is/v1/invoices', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer: 'SJS',
    template: 'INVOICE R2 FULLY FUNCTIONAL',
    memo: 'PS-7310',
    lineItems: [
      {
        item: 'IPHONE 12',
        description: '128GB-BLACK C(AMZ)',
        quantity: 1,
        rate: 100.00,
        serialNumber: '353222108267157'
      }
    ]
  })
});
```

### Capabilities
| Feature | Supported |
|---------|-----------|
| Create Invoices | ✅ Yes |
| Create Credit Memos | ✅ Yes |
| Create Bill Credits | ✅ Yes |
| Create Item Receipts | ✅ Yes |
| Query Data | ✅ Yes |
| Custom Fields | ✅ Yes |
| Serial Numbers | ⚠️ Verify |
| Templates | ✅ Yes |
| Webhooks | ✅ Yes |

### Pros
- ✅ **Modern REST API** — JSON, not XML
- ✅ **Easy to integrate** — standard HTTP calls
- ✅ **Good documentation** — developer-friendly
- ✅ **Enterprise supported** — confirmed
- ✅ **Near real-time** — via local agent
- ✅ **Any language** — just HTTP calls

### Cons
- ❌ **Monthly cost** — subscription required
- ❌ **Third-party dependency** — reliant on Conductor
- ❌ **Internet required** — cloud-based routing
- ❌ **Agent required** — must run on QB machine
- ❌ **Rate limits** — API call limits on plans

### Pricing
| Plan | Price | API Calls |
|------|-------|-----------|
| Starter | ~$49/mo | Limited |
| Professional | ~$99/mo | Higher |
| Enterprise | Custom | Unlimited |

*Verify current pricing at conductor.is*

### Links
- Website: https://conductor.is/
- Documentation: https://docs.conductor.is/
- API Reference: https://api.conductor.is/docs

---

## Option 4: Transaction Pro

### Overview
A desktop import/export tool for QuickBooks Desktop that allows bulk import from Excel/CSV files.

### Technical Details
- **Type:** Desktop application
- **Import formats:** Excel, CSV, IIF, XML
- **Operation:** Manual or scheduled via command line

### How It Works
```
┌─────────────────┐                ┌─────────────────┐               ┌─────────────┐
│   Excel/CSV     │ → Import →     │  Transaction    │ → Direct →    │  QuickBooks │
│   Packing Slip  │                │  Pro Importer   │               │  Enterprise │
└─────────────────┘                └─────────────────┘               └─────────────┘
```

### Requirements
- Windows
- QuickBooks Desktop
- Transaction Pro license
- Excel/CSV files formatted to their spec

### Capabilities
| Feature | Supported |
|---------|-----------|
| Import Invoices | ✅ Yes |
| Import Credit Memos | ✅ Yes |
| Import Bills | ✅ Yes |
| Import Purchase Orders | ✅ Yes |
| Import Items | ✅ Yes |
| Import Customers | ✅ Yes |
| Field Mapping | ✅ Yes (UI) |
| Scheduling | ✅ Yes (command line) |
| Templates | ⚠️ May need setup |

### Automation Potential
Can be automated via command-line interface:
```bash
TransactionPro.exe /import "C:\PackingSlips\PS-7310.csv" /profile "Invoice Import"
```

### Pros
- ✅ **No coding** — GUI-based
- ✅ **Excel native** — works with your existing format
- ✅ **One-time cost** — not subscription
- ✅ **Enterprise supported** — confirmed
- ✅ **Field mapping** — visual mapper
- ✅ **Can be scheduled** — via command line

### Cons
- ❌ **Semi-manual** — requires human trigger (unless scripted)
- ❌ **Windows only** — desktop app
- ❌ **Initial setup** — mapping configuration
- ❌ **Per-seat license** — cost per user
- ❌ **Not real-time** — batch process

### Pricing
| Product | Price |
|---------|-------|
| Importer | ~$200 |
| Importer + Exporter | ~$350 |
| Enterprise Bundle | ~$400+ |

*One-time purchase, verify current pricing*

### Links
- Website: https://www.intuit.com/partners/transaction-pro/
- Also: https://transactionpro.com/

---

## Option 5: SaaSAnt

### Overview
An Excel add-in that provides direct import/export capabilities with QuickBooks Desktop.

### Technical Details
- **Type:** Excel Add-in
- **Interface:** Excel ribbon integration
- **Operation:** Manual button click

### How It Works
```
┌─────────────────┐                ┌─────────────────┐               ┌─────────────┐
│   Excel with    │ → Click →      │   SaaSAnt       │ → Direct →    │  QuickBooks │
│   SaaSAnt       │   Import       │   Add-in        │               │  Enterprise │
└─────────────────┘                └─────────────────┘               └─────────────┘
```

### Requirements
- Windows
- Microsoft Excel
- QuickBooks Desktop
- SaaSAnt subscription

### Capabilities
| Feature | Supported |
|---------|-----------|
| Import Invoices | ✅ Yes |
| Export Invoices | ✅ Yes |
| Import Credit Memos | ✅ Yes |
| Import Bill Credits | ✅ Yes |
| Import Items | ✅ Yes |
| Two-way Sync | ✅ Yes |
| Templates | ✅ Yes |
| Custom Fields | ✅ Yes |

### Pros
- ✅ **Excel-native** — work in familiar environment
- ✅ **No coding** — point and click
- ✅ **Two-way sync** — import and export
- ✅ **Enterprise supported** — confirmed
- ✅ **Good templates** — pre-built formats
- ✅ **Affordable** — reasonable subscription

### Cons
- ❌ **Manual trigger** — click button each time
- ❌ **Windows + Excel only** — environment locked
- ❌ **Subscription** — ongoing cost
- ❌ **Not automatable** — no command line/API
- ❌ **Excel dependency** — must use Excel

### Pricing
| Plan | Price |
|------|-------|
| Basic | ~$30/mo |
| Pro | ~$50/mo |
| Team | Custom |

*Verify current pricing at saasant.com*

### Links
- Website: https://www.saasant.com/
- QuickBooks Desktop Product: https://www.saasant.com/quickbooks-desktop/

---

## Option 6: Coefficient

### Overview
A spreadsheet-based data platform that connects Google Sheets/Excel to various data sources including some accounting systems.

### Technical Details
- **Type:** Spreadsheet add-on (Google Sheets / Excel)
- **Approach:** SQL-like queries to data sources
- **Sync:** Scheduled or manual

### ⚠️ Critical Verification Needed
**Must confirm if Coefficient supports QuickBooks Desktop/Enterprise or only QuickBooks Online.**

Most spreadsheet tools only support QuickBooks Online due to its REST API.

### How It Would Work (if supported)
```
┌─────────────────┐                ┌─────────────────┐               ┌─────────────┐
│   Google Sheets │ ←── Sync ──→   │   Coefficient   │ ←── ? ──→     │  QuickBooks │
│   / Excel       │                │   Platform      │               │  Enterprise │
└─────────────────┘                └─────────────────┘               └─────────────┘
```

### Capabilities (if Desktop supported)
| Feature | Likely Support |
|---------|---------------|
| Read Data | ⚠️ Verify |
| Write Invoices | ⚠️ Verify |
| Two-way Sync | ⚠️ Verify |
| SQL-like Queries | ✅ Yes (their feature) |
| Scheduled Refresh | ✅ Yes |

### Pros (if it works)
- ✅ **Spreadsheet native** — familiar interface
- ✅ **SQL-like** — easy queries
- ✅ **Free tier** — available
- ✅ **Modern UX** — clean interface

### Cons / Risks
- ❌ **Desktop support uncertain** — likely Online only
- ❌ **Limited write capability** — often read-focused
- ❌ **Third-party dependency**
- ❌ **May not support invoice creation**

### Pricing
| Plan | Price |
|------|-------|
| Free | $0 (limited) |
| Starter | ~$49/mo |
| Pro | ~$99/mo |

### Action Required
**→ Must verify Desktop Enterprise support before considering**

### Links
- Website: https://coefficient.io/
- Integrations: Check their integrations page for QuickBooks Desktop

---

## Option 7: Apix Drive

### Overview
An iPaaS (Integration Platform as a Service) that connects various apps through automated workflows.

### Technical Details
- **Type:** Cloud-based integration platform
- **Approach:** Trigger → Action workflows
- **Interface:** Visual workflow builder

### ⚠️ Desktop Support Status
**Uncertain** — Most iPaaS platforms only support QuickBooks Online.

### How It Would Work (if supported)
```
┌─────────────────┐                ┌─────────────────┐               ┌─────────────┐
│   Trigger       │ → Workflow →   │   Apix Drive    │ → Action →    │  QuickBooks │
│   (New Excel)   │                │   Platform      │               │  Enterprise │
└─────────────────┘                └─────────────────┘               └─────────────┘
```

### Capabilities (if supported)
| Feature | Likely Support |
|---------|---------------|
| Create Invoices | ⚠️ Verify |
| File Triggers | ✅ Yes |
| Scheduled Workflows | ✅ Yes |
| Multi-step Workflows | ✅ Yes |

### Pros
- ✅ **No coding** — visual builder
- ✅ **Affordable** — lower cost
- ✅ **Many integrations** — connect other apps

### Cons
- ❌ **Desktop support unlikely** — verify
- ❌ **Third-party dependency**
- ❌ **Learning curve** — new platform

### Pricing
| Plan | Price |
|------|-------|
| Free | Limited |
| Basic | ~$20/mo |
| Pro | ~$50/mo |

### Action Required
**→ Must verify Desktop Enterprise support**

### Links
- Website: https://apix-drive.com/

---

## Option 8: FinJinni

### Overview
A financial automation platform focused on accounting workflows.

### Technical Details
- **Type:** Accounting automation platform
- **Focus:** Financial document processing

### ⚠️ Desktop Support Status
**Unknown** — requires verification.

### Capabilities (claimed)
| Feature | Status |
|---------|--------|
| Invoice Automation | ✅ Claimed |
| AP Automation | ✅ Claimed |
| Bank Reconciliation | ✅ Claimed |
| QuickBooks Integration | ⚠️ Version unclear |

### Pros
- ✅ **Accounting focused** — built for this use case
- ✅ **Document processing** — may handle packing slips

### Cons
- ❌ **Desktop support unclear**
- ❌ **Enterprise pricing** — contact sales
- ❌ **Less documentation** — harder to evaluate

### Action Required
**→ Contact FinJinni to verify QuickBooks Desktop Enterprise support**

### Links
- Website: https://finjinni.com/

---

## Option 9: DBSync

### Overview
An enterprise data integration platform with specific QuickBooks Desktop support.

### Technical Details
- **Type:** Enterprise integration platform
- **Approach:** Bi-directional sync
- **Desktop Support:** ✅ Confirmed

### How It Works
```
┌─────────────────┐                ┌─────────────────┐               ┌─────────────┐
│   Your Data     │ ←── Sync ──→   │   DBSync        │ ←── qbXML ──→ │  QuickBooks │
│   (CRM/ERP/DB)  │                │   Platform      │               │  Enterprise │
└─────────────────┘                └─────────────────┘               └─────────────┘
```

### Capabilities
| Feature | Supported |
|---------|-----------|
| Create Invoices | ✅ Yes |
| Bi-directional Sync | ✅ Yes |
| Field Mapping | ✅ Yes |
| Scheduled Sync | ✅ Yes |
| Multiple Sources | ✅ Yes (Salesforce, etc.) |

### Pros
- ✅ **Enterprise grade** — robust platform
- ✅ **Desktop confirmed** — works with Enterprise
- ✅ **Bi-directional** — read and write
- ✅ **Multiple connectors** — expandable

### Cons
- ❌ **Enterprise pricing** — higher cost
- ❌ **Complex setup** — overkill for simple use case
- ❌ **May need implementation help**

### Pricing
| Plan | Price |
|------|-------|
| Professional | ~$50/mo |
| Enterprise | ~$100-200/mo |

### Links
- Website: https://www.dbsync.com/
- QuickBooks: https://www.dbsync.com/quickbooks-integration/

---

## Option 10: Python Library (selfjared1/quickbooks_desktop) {#option-10-python-library}

### Overview
An open-source Python library that wraps the QuickBooks Desktop SDK, converting Python objects to qbXML automatically.

### Technical Details
- **Language:** Python
- **Communication:** win32com to QBXMLRP2 (same as SDK)
- **Approach:** Python dataclasses converted to qbXML

### How It Works
```
┌─────────────────┐                ┌─────────────────┐               ┌─────────────┐
│   Your Python   │ → Dataclass →  │   Library       │ → qbXML →     │  QuickBooks │
│   Code          │                │   (win32com)    │               │  Enterprise │
└─────────────────┘                └─────────────────┘               └─────────────┘
```

### Requirements
- Windows
- Python (32-bit for QB pre-2022, 64-bit for QB 2022+)
- QuickBooks Desktop running with company file open
- Dependencies: win32com, lxml

### Code Example
```python
from quickbooks_desktop import QuickbooksDesktop
from quickbooks_desktop.transactions.invoices import Invoice, InvoiceLineAdd
from quickbooks_desktop.lists import CustomerRef, ItemRef, TemplateRef

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

### Capabilities
| Feature | Supported |
|---------|-----------|
| Create Invoices | Yes |
| Serial Numbers | Yes (built-in field) |
| Templates | Yes |
| Credit Memos | Yes |
| Bill Credits | Yes |
| Purchase Orders | Yes |
| Item Receipts | Yes |
| Batch Operations | Yes (loop) |

### Pros
- Free and open source
- Python is easier than raw qbXML
- Serial number field already exists
- Handles XML generation automatically
- Well-structured with dataclasses
- Supports all major transactions

### Cons
- Windows only
- Python 32-bit required for older QB
- QuickBooks must be running
- Less documentation than official SDK
- Smaller community than commercial tools
- May have bugs (less tested than official SDK)

### Pricing
- **Free** (MIT License)

### Links
- Repo: https://github.com/selfjared1/quickbooks_desktop
- See: REPO-ANALYSIS-quickbooks-desktop.md for detailed breakdown

---

## Comparison Matrix

### Enterprise Desktop Support

| Option | Confirmed | Verification Needed |
|--------|-----------|---------------------|
| QBSDK | ✅ Yes | — |
| QBWC | ✅ Yes | — |
| Conductor | ✅ Yes | — |
| Transaction Pro | ✅ Yes | — |
| SaaSAnt | ✅ Yes | — |
| Coefficient | ❓ | **Must verify** |
| Apix Drive | ❓ | **Must verify** |
| FinJinni | ❓ | **Must verify** |
| DBSync | ✅ Yes | — |
| Python Library | ✅ Yes | — |

### Automation Level

| Option | Full Auto | Semi-Auto | Manual |
|--------|-----------|-----------|--------|
| QBSDK | ✅ | — | — |
| QBWC | ✅ | — | — |
| Conductor | ✅ | — | — |
| Transaction Pro | ⚠️ (scripted) | ✅ | — |
| SaaSAnt | — | — | ✅ |
| Coefficient | — | ✅ | — |
| Apix Drive | ✅ | — | — |
| FinJinni | ✅ | — | — |
| DBSync | ✅ | — | — |
| Python Library | ✅ | — | — |

### Cost Comparison

| Option | Type | Monthly | One-Time | Free Tier |
|--------|------|---------|----------|-----------|
| QBSDK | Free | $0 | $0 | ✅ |
| QBWC | Free | $0 | $0 | ✅ |
| Conductor | Subscription | ~$50-100 | — | ❌ |
| Transaction Pro | One-time | — | ~$200-400 | ❌ |
| SaaSAnt | Subscription | ~$30-50 | — | ❌ |
| Coefficient | Subscription | ~$0-99 | — | ✅ |
| Apix Drive | Subscription | ~$20-50 | — | ✅ |
| FinJinni | Enterprise | Contact | — | ❌ |
| DBSync | Subscription | ~$50-200 | — | ❌ |
| Python Library | Free | $0 | $0 | ✅ |

### Development Effort

| Option | Coding Required | Complexity | Time to Deploy |
|--------|-----------------|------------|----------------|
| QBSDK | Heavy | High | Weeks |
| QBWC | Heavy | High | Weeks |
| Conductor | Medium | Medium | Days |
| Transaction Pro | None | Low | Hours |
| SaaSAnt | None | Low | Hours |
| Coefficient | None | Low | Hours |
| Apix Drive | Low | Medium | Days |
| FinJinni | Low | Medium | Days |
| DBSync | Low-Medium | Medium | Days |
| Python Library | Medium | Medium | Days |

---

## Decision Criteria

### If Priority is **No Coding**
**→ Transaction Pro or SaaSAnt**
- Both work with Excel
- Both confirmed for Enterprise
- Trade-off: Semi-manual process

### If Priority is **Full Automation + Easy Development**
**→ Conductor**
- REST API (modern, easy)
- Enterprise confirmed
- Trade-off: Monthly subscription

### If Priority is **Full Automation + No Cost**
**→ Python Library (selfjared1/quickbooks_desktop)**
- Free
- Easier than raw qbXML (Python dataclasses)
- Serial number support built-in
- Trade-off: Windows + Python required, less documentation

**Fallback: QBSDK or QBWC**
- Free
- Full control
- Trade-off: Complex development (raw qbXML)

### If Priority is **Enterprise Grade + Expandable**
**→ DBSync**
- Robust platform
- Multiple integrations
- Trade-off: Higher cost, complexity

### If Priority is **Quick Test**
**→ Transaction Pro (trial) or SaaSAnt (trial)**
- Get working quickly
- Validate workflow
- Then decide on full automation

---

## Open Questions

### Must Verify
- [ ] Does **Coefficient** support QuickBooks Desktop Enterprise?
- [ ] Does **Apix Drive** support QuickBooks Desktop Enterprise?
- [ ] Does **FinJinni** support QuickBooks Desktop Enterprise?
- [ ] Does **Conductor** support the Serial Number field?

### Business Questions
- [ ] What is the acceptable cost per month?
- [ ] How important is full automation vs. semi-manual?
- [ ] Who will maintain the integration?
- [ ] Is coding capability available in-house?
- [ ] What is the timeline for implementation?
- [ ] How many packing slips per day/week?

### Technical Questions
- [ ] Where will the Excel packing slips be stored? (Local folder, cloud, email?)
- [ ] What triggers the invoice creation? (File drop, schedule, manual?)
- [ ] Are all customers already in QuickBooks?
- [ ] Are all items (IPHONE 12, etc.) already in QuickBooks?
- [ ] Where does pricing (RATE) come from?

---

## Recommendation for Agent

**Before choosing, verify:**
1. Coefficient Desktop support → if yes, test it (free tier)
2. If no → narrow to confirmed options

**Suggested evaluation order:**
1. **Conductor** — if budget allows, easiest path to full automation
2. **Transaction Pro** — if no-code is priority, one-time cost
3. **QBWC** — if free is priority and coding is available

**Prototype suggestion:**
Start with **Transaction Pro trial** to validate the Excel → Invoice workflow works, then decide if full automation (Conductor/QBWC) is worth the investment.

---

*Last updated: January 5, 2026*
