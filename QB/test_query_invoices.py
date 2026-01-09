"""
Step 3: Query Invoices from QuickBooks
This shows the invoice structure before we try creating one.
"""
from quickbooks_desktop.session_manager import SessionManager


# qbXML request to get recent invoices
INVOICE_QUERY_XML = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceQueryRq>
      <MaxReturned>5</MaxReturned>
      <IncludeLineItems>true</IncludeLineItems>
    </InvoiceQueryRq>
  </QBXMLMsgsRq>
</QBXML>
"""


if __name__ == '__main__':
    qb = SessionManager(application_name="AutomationTest")
    
    try:
        # Connect
        qb.open_connection()
        print("✓ Connected to QuickBooks")
        
        qb.begin_session()
        print("✓ Session started")
        
        # Query invoices
        print("\nQuerying invoices...")
        response = qb.send_xml(INVOICE_QUERY_XML)
        
        print("\n" + "="*50)
        print("RAW RESPONSE:")
        print("="*50)
        print(response)
        print("="*50)
        
        # The response shows the invoice structure
        # Look for: CustomerRef, TemplateRef, TxnDate, InvoiceLine, etc.
        # This will inform how to build InvoiceAdd requests
        
    except Exception as e:
        print(f"ERROR: {e}")
        
    finally:
        qb.close_qb()
        print("\n✓ Connection closed")
