"""
Step 2: Query Customers from QuickBooks
This confirms we can READ data, not just connect.
"""
from quickbooks_desktop.session_manager import SessionManager


# qbXML request to get first 10 customers
CUSTOMER_QUERY_XML = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq>
      <MaxReturned>10</MaxReturned>
    </CustomerQueryRq>
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
        
        # Query customers
        print("\nQuerying customers...")
        response = qb.send_xml(CUSTOMER_QUERY_XML)
        
        print("\n" + "="*50)
        print("RAW RESPONSE:")
        print("="*50)
        print(response)
        print("="*50)
        
        # If you want to count customers found, you can parse the XML
        # For now, just seeing the raw response confirms the query works
        
    except Exception as e:
        print(f"ERROR: {e}")
        
    finally:
        qb.close_qb()
        print("\n✓ Connection closed")
