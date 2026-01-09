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
    """Build qbXML for creating an invoice."""
    
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
    
    return f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
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
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>
"""


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
    
    # Build the XML request
    invoice_xml = build_invoice_add_xml(
        customer_name=CUSTOMER_NAME,
        item_name=ITEM_NAME,
        description=DESCRIPTION,
        quantity=QUANTITY,
        rate=RATE,
        memo=MEMO,
        serial_number=SERIAL_NUMBER,
        template_name=TEMPLATE_NAME
    )
    
    print("Invoice XML to send:")
    print(invoice_xml)
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
        response = qb.send_xml(invoice_xml)
        
        print("\n" + "="*50)
        print("RESPONSE:")
        print("="*50)
        print(response)
        print("="*50)
        
        # Check for success
        if "<InvoiceAddRs statusCode=\"0\"" in response:
            print("\n✅ INVOICE CREATED SUCCESSFULLY!")
        elif "statusCode=\"0\"" in response:
            print("\n✅ Request successful!")
        else:
            print("\n⚠️  Check the response for errors")
        
    except Exception as e:
        print(f"ERROR: {e}")
        
    finally:
        qb.close_qb()
        print("\n✓ Connection closed")
