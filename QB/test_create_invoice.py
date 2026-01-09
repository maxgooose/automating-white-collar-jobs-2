"""
Step 4: Create a Test Invoice in QuickBooks
Run this AFTER queries work. Use a TEST customer first!

BEFORE RUNNING:
- Make sure "Test Customer" exists in QuickBooks (or change the name below)
- Make sure a test item exists (or change "Test Item" below)
"""
from quickbooks_desktop.session_manager import SessionManager
from datetime import date


def build_invoice_add_xml(
    customer_name: str,
    item_name: str,
    description: str,
    quantity: int,
    rate: float,
    memo: str = "",
    serial_number: str = "",
    template_name: str = ""
) -> str:
    """Build the InvoiceAddRq body (without envelope)."""
    
    # Template line (optional)
    template_line = ""
    if template_name:
        template_line = f"""
        <TemplateRef>
          <FullName>{template_name}</FullName>
        </TemplateRef>"""
    
    # Serial number line (optional)
    serial_line = ""
    if serial_number:
        serial_line = f"<SerialNumber>{serial_number}</SerialNumber>"
    
    return f"""<InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>{customer_name}</FullName>
        </CustomerRef>{template_line}
        <TxnDate>{date.today().isoformat()}</TxnDate>
        <Memo>{memo}</Memo>
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{item_name}</FullName>
          </ItemRef>
          <Desc>{description}</Desc>
          <Quantity>{quantity}</Quantity>
          <Rate>{rate:.2f}</Rate>
          {serial_line}
        </InvoiceLineAdd>
      </InvoiceAdd>
    </InvoiceAddRq>"""


if __name__ == '__main__':
    # ========================================
    # CONFIGURE THESE FOR YOUR TEST
    # ========================================
    CUSTOMER_NAME = "Test Customer"  # Must exist in QB
    ITEM_NAME = "Test Item"          # Must exist in QB Items
    DESCRIPTION = "Test invoice from automation script"
    QUANTITY = 1
    RATE = 10.00
    MEMO = "AUTOMATION-TEST"
    SERIAL_NUMBER = ""  # Leave empty for first test
    TEMPLATE_NAME = ""  # Leave empty to use default template
    # ========================================
    
    # Build the request body
    invoice_body = build_invoice_add_xml(
        customer_name=CUSTOMER_NAME,
        item_name=ITEM_NAME,
        description=DESCRIPTION,
        quantity=QUANTITY,
        rate=RATE,
        memo=MEMO,
        serial_number=SERIAL_NUMBER,
        template_name=TEMPLATE_NAME
    )
    
    # Build full envelope
    full_request = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    {invoice_body}
  </QBXMLMsgsRq>
</QBXML>"""
    
    print("Invoice XML to send:")
    print(full_request)
    print("\n" + "="*50)
    
    # Confirm before running
    confirm = input("Create this invoice? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        exit()
    
    qb = SessionManager(application_name="AutomationTest")
    
    try:
        qb.open_connection()
        print("✓ Connected to QuickBooks")
        
        qb.begin_session()
        print("✓ Session started")
        
        print("\nCreating invoice...")
        response = qb.qbXMLRP.ProcessRequest(qb.ticket, full_request)
        
        print("\n" + "="*50)
        print("RESPONSE:")
        print("="*50)
        print(response)
        print("="*50)
        
        # Check for success
        if 'statusCode="0"' in response:
            print("\n✅ INVOICE CREATED SUCCESSFULLY!")
        else:
            print("\n⚠️  Check the response for errors")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if qb.session_begun:
            qb.end_session()
        if qb.connection_open:
            qb.close_connection()
        print("\n✓ Connection closed")
