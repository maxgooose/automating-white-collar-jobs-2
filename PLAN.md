# QuickBooks Enterprise Automation Plan

## Project Overview

Automating the creation of QuickBooks invoices from Excel packing slips for **Universal Cellular** using QuickBooks Enterprise Desktop.

---

## Current Workflow (Manual)

```mermaid
graph LR
    A[Excel Packing Slip] --> B[Manual Data Entry]
    B --> C[QuickBooks Invoice]
```

**Pain Points:**
- Manual entry of up to 250 IMEIs per packing slip
- Time-consuming and error-prone
- Multiple document types to create (invoices, credit memos, bill credits)

---

## Target Workflow (Automated)

```mermaid
graph LR
    A[Excel Packing Slip] --> B[Automation Script]
    B --> C[QuickBooks API/SDK]
    C --> D[Invoice Created Automatically]
```

---

## Document Mappings

| Input Document | QuickBooks Output |
|----------------|-------------------|
| Packing Slips | Invoice |
| Receiving Reports | Item Receipt / Receive Inventory |
| RMA IN | Credit Memo |
| RMA OUT | Bill Credit |
| Vendor Receiving | Item Receipt |
| Vendor Returning | Bill Credit |

---

## Data Structure

### Packing Slip (Excel) Fields

| Field | Description | Example |
|-------|-------------|---------|
| CUSTOMER | Customer name | SJS |
| P.S. | Packing Slip number | 7310 |
| MODEL / PART NUMBER | Device model | IPHONE 12 |
| DESCRIPTION | Storage + Color | 128GB-BLACK |
| IMEI / SERIAL NUMBER | 15-digit IMEI | 353222108267157 |
| QTY | Quantity | 1 |
| OBSERVATION | Notes | (optional) |
| GRADE | Condition grade | C, C(AMZ) |

### QuickBooks Invoice Fields

| Field | Maps From | Notes |
|-------|-----------|-------|
| CUSTOMER:JOB | CUSTOMER | Must exist in QB |
| TEMPLATE | - | "INVOICE R2 FULLY FUNCTIONAL" |
| ITEM | MODEL / PART NUMBER | Must exist in QB Items |
| QTY | QTY | Usually 1 per IMEI |
| SERIAL NUMBER | IMEI / SERIAL NUMBER | Custom field |
| GRADING / DESCRIPTION | DESCRIPTION + GRADE | Combined |
| RATE | Pricing lookup | From QB or input |
| AMOUNT | QTY × RATE | Calculated |
| MEMO | P.S. # | Reference link |

---

## Technical Options

### Option A: QuickBooks SDK (QBSDK)

**Pros:**
- Full control over all QuickBooks features
- Free to use
- Works with Desktop/Enterprise

**Cons:**
- Requires QB running on same machine
- XML-based (qbXML) - more complex
- Local only

**Languages:** Node.js, C#, VB.NET

### Option B: QuickBooks Web Connector (QBWC)

**Pros:**
- Web-based integration
- QB doesn't need to be open constantly
- Scheduled syncs

**Cons:**
- SOAP/XML complexity
- Not real-time

### Option C: Third-Party Tools

| Tool | Type | Desktop Support | Notes |
|------|------|-----------------|-------|
| **Coefficient** | REST API / Spreadsheet | ⚠️ Verify | Current winner - needs verification |
| Transaction Pro | Import tool | ✅ Yes | CSV/Excel import |
| SaaSAnt | Import/Export | ✅ Yes | Excel-based |
| Conductor | API | ✅ Yes | REST API wrapper |
| Apix Drive | Integration | ⚠️ Check | iPaaS |
| FinJinni | Accounting | ⚠️ Check | Financial focus |

---

## Recommended Approach

### Phase 1: Excel Parser
1. Read Excel packing slip
2. Parse all rows (up to 250 IMEIs)
3. Validate data structure
4. Output structured JSON for QB

### Phase 2: QuickBooks Connection
1. Set up QBSDK or Web Connector
2. Authenticate with QuickBooks
3. Test simple invoice creation

### Phase 3: Invoice Automation
1. Map parsed data to invoice fields
2. Handle batch creation (multiple IMEIs)
3. Use correct template
4. Add error handling

### Phase 4: Expand to Other Documents
1. Credit Memos (RMA IN)
2. Bill Credits (RMA OUT)
3. Item Receipts (Receiving)

---

## File Structure

```
automating-white-collar-jobs-2/
├── PLAN.md                 # This file
├── src/
│   ├── parser/             # Excel parsing logic
│   ├── quickbooks/         # QB SDK/API integration
│   └── utils/              # Helper functions
├── templates/
│   └── sample_packing_slip.xlsx
├── config/
│   └── field_mappings.json
└── tests/
    └── sample_data/
```

---

## Environment Requirements

- **QuickBooks Enterprise** (installed and running for SDK)
- **QuickBooks Web Connector** (if using web approach)
- **Node.js** or **C#/.NET** runtime
- **Excel files** (packing slips as input)

---

## Next Steps

- [ ] Verify Coefficient supports QuickBooks Desktop Enterprise
- [ ] If yes → Explore Coefficient REST API approach
- [ ] If no → Set up QBSDK development environment
- [ ] Create Excel parser for packing slip format
- [ ] Build proof-of-concept: single invoice creation
- [ ] Test with real packing slip data
- [ ] Scale to batch processing (250 IMEIs)

---

## Questions to Resolve

1. **Pricing:** Where does RATE come from? (QB item price, separate lookup, manual?)
2. **Customer matching:** Are all customers already in QuickBooks?
3. **Item matching:** Are all MODEL/PART NUMBERs already in QuickBooks Items?
4. **Error handling:** What happens if an IMEI already exists?
5. **Validation:** Any business rules for grades, quantities?

---

## Reference

- QuickBooks SDK Documentation: https://developer.intuit.com/
- qbXML Reference: Built into SDK
- Template in use: **INVOICE R2 FULLY FUNCTIONAL**
- **[RESEARCH-OPTIONS.md](./RESEARCH-OPTIONS.md)** — Deep dive on all integration options
