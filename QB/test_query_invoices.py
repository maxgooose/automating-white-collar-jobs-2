"""
Step 3: Query Invoices from QuickBooks
This shows the invoice structure before we try creating one.
"""
from quickbooks_desktop.session_manager import SessionManager


# qbXML request to get recent invoices (just the request body)
INVOICE_QUERY_XML = """<InvoiceQueryRq>
  <MaxReturned>5</MaxReturned>
  <IncludeLineItems>true</IncludeLineItems>
</InvoiceQueryRq>"""


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
        
        # Build the full request envelope
        full_request = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    {INVOICE_QUERY_XML}
  </QBXMLMsgsRq>
</QBXML>"""
        
        # Send directly via the processor
        response = qb.qbXMLRP.ProcessRequest(qb.ticket, full_request)
        
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
        import traceback
        traceback.print_exc()
        
    finally:
        if qb.session_begun:
            qb.end_session()
        if qb.connection_open:
            qb.close_connection()
        print("\n✓ Connection closed")
