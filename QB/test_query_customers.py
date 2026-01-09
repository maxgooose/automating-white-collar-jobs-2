"""
Step 2: Query Customers from QuickBooks
This confirms we can READ data, not just connect.
"""
from quickbooks_desktop.session_manager import SessionManager


# qbXML request to get first 10 customers (just the request body, not full envelope)
CUSTOMER_QUERY_XML = """<CustomerQueryRq>
  <MaxReturned>10</MaxReturned>
</CustomerQueryRq>"""


if __name__ == '__main__':
    qb = SessionManager(application_name="AutomationTest")
    
    try:
        # Connect
        qb.open_connection()
        print("✓ Connected to QuickBooks")
        
        qb.begin_session()
        print("✓ Session started")
        
        # Query customers - send raw XML via the processor
        print("\nQuerying customers...")
        
        # Build the full request envelope
        full_request = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    {CUSTOMER_QUERY_XML}
  </QBXMLMsgsRq>
</QBXML>"""
        
        # Send directly via the processor
        response = qb.qbXMLRP.ProcessRequest(qb.ticket, full_request)
        
        print("\n" + "="*50)
        print("RAW RESPONSE:")
        print("="*50)
        print(response)
        print("="*50)
        
        # If you want to count customers found, you can parse the XML
        # For now, just seeing the raw response confirms the query works
        
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
