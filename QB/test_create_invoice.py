"""
Step 4: Create a Test Invoice in QuickBooks
Automatically finds a real customer and item from QB, then creates an invoice.
"""
from quickbooks_desktop.session_manager import SessionManager
from datetime import date
import re


def query_first_customer(qb):
    """Get the first customer name from QuickBooks."""
    xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq><MaxReturned>1</MaxReturned></CustomerQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    response = qb.qbXMLRP.ProcessRequest(qb.ticket, xml)
    match = re.search(r'<FullName>([^<]+)</FullName>', response)
    return match.group(1) if match else None


def query_first_item(qb):
    """Get the first service/inventory item from QuickBooks."""
    xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemQueryRq><MaxReturned>5</MaxReturned></ItemQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    response = qb.qbXMLRP.ProcessRequest(qb.ticket, xml)
    # Find item names (skip subtotals, discounts, etc.)
    matches = re.findall(r'<FullName>([^<]+)</FullName>', response)
    return matches[0] if matches else None


if __name__ == '__main__':
    qb = SessionManager(application_name="AutomationTest")
    
    try:
        qb.open_connection()
        print("✓ Connected to QuickBooks")
        
        qb.begin_session()
        print("✓ Session started")
        
        # Find real customer and item
        print("\nFinding customer and item...")
        customer_name = query_first_customer(qb)
        item_name = query_first_item(qb)
        
        if not customer_name:
            print("❌ No customers found in QuickBooks!")
            exit(1)
        if not item_name:
            print("❌ No items found in QuickBooks!")
            exit(1)
            
        print(f"  Customer: {customer_name}")
        print(f"  Item: {item_name}")
        
        # Build invoice
        invoice_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>{customer_name}</FullName>
        </CustomerRef>
        <TxnDate>{date.today().isoformat()}</TxnDate>
        <Memo>AUTOMATION-TEST</Memo>
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{item_name}</FullName>
          </ItemRef>
          <Desc>Test from automation</Desc>
          <Quantity>1</Quantity>
          <Rate>10.00</Rate>
        </InvoiceLineAdd>
      </InvoiceAdd>
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
        
        print("\n" + "="*50)
        confirm = input(f"Create invoice for {customer_name} with {item_name}? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            exit()
        
        print("\nCreating invoice...")
        response = qb.qbXMLRP.ProcessRequest(qb.ticket, invoice_xml)
        
        print("\n" + "="*50)
        print("RESPONSE:")
        print("="*50)
        print(response)
        print("="*50)
        
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
