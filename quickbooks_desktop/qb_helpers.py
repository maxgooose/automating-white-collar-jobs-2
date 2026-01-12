"""
QuickBooks Desktop helper functions.
High-level operations built on top of SessionManager.
"""
import re
from .session_manager import SessionManager


def test_connection():
    """
    Test basic QB connection (open, begin session, close).
    
    Returns:
        dict with success, message, and details
    """
    qb = SessionManager()
    steps = []
    
    try:
        # Step 1: Open connection
        qb.open_connection()
        steps.append("✓ Connection opened")
        
        # Step 2: Begin session
        qb.begin_session()
        steps.append("✓ Session started")
        
        # Step 3: Close
        qb.close_qb()
        steps.append("✓ Connection closed")
        
        return {
            'success': True,
            'message': 'QuickBooks connection successful!',
            'steps': steps
        }
        
    except Exception as e:
        steps.append(f"✗ Error: {str(e)}")
        return {
            'success': False,
            'message': str(e),
            'steps': steps
        }
    finally:
        if qb.connection_open:
            qb.close_qb()


def query_customers(max_returned=10):
    """
    Query customers from QuickBooks.
    
    Args:
        max_returned: Maximum number of customers to return
        
    Returns:
        dict with success, customers list, and raw response
    """
    qb = SessionManager()
    
    try:
        qb.open_connection()
        qb.begin_session()
        
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq>
      <MaxReturned>{max_returned}</MaxReturned>
    </CustomerQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
        
        response = qb.send_request(xml)
        
        # Parse customer names from response
        customers = re.findall(r'<FullName>([^<]+)</FullName>', response)
        
        return {
            'success': True,
            'message': f'Found {len(customers)} customer(s)',
            'customers': customers,
            'raw_response': response[:2000] if len(response) > 2000 else response
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'customers': [],
            'raw_response': ''
        }
    finally:
        if qb.connection_open:
            qb.close_qb()


def query_invoices(max_returned=10):
    """
    Query recent invoices from QuickBooks.
    
    Args:
        max_returned: Maximum number of invoices to return
        
    Returns:
        dict with success, invoices list, and raw response
    """
    qb = SessionManager()
    
    try:
        qb.open_connection()
        qb.begin_session()
        
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceQueryRq>
      <MaxReturned>{max_returned}</MaxReturned>
    </InvoiceQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
        
        response = qb.send_request(xml)
        
        # Parse invoice details from response
        invoices = []
        
        # Find all TxnID and RefNumber pairs
        txn_ids = re.findall(r'<TxnID>([^<]+)</TxnID>', response)
        ref_numbers = re.findall(r'<RefNumber>([^<]+)</RefNumber>', response)
        txn_dates = re.findall(r'<TxnDate>([^<]+)</TxnDate>', response)
        
        for i in range(min(len(txn_ids), len(ref_numbers))):
            invoices.append({
                'txn_id': txn_ids[i] if i < len(txn_ids) else 'N/A',
                'ref_number': ref_numbers[i] if i < len(ref_numbers) else 'N/A',
                'date': txn_dates[i] if i < len(txn_dates) else 'N/A'
            })
        
        return {
            'success': True,
            'message': f'Found {len(invoices)} invoice(s)',
            'invoices': invoices,
            'raw_response': response[:2000] if len(response) > 2000 else response
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'invoices': [],
            'raw_response': ''
        }
    finally:
        if qb.connection_open:
            qb.close_qb()


def check_entity_exists(qb, entity_type, name):
    """
    Check if a customer or item exists in QuickBooks.
    
    Args:
        qb: Active SessionManager instance
        entity_type: 'customer' or 'item'
        name: Entity name to check
        
    Returns:
        bool indicating if entity exists
    """
    if entity_type == "customer":
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq>
      <FullName>{name}</FullName>
    </CustomerQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    else:  # item
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemQueryRq>
      <FullName>{name}</FullName>
    </ItemQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    
    response = qb.send_request(xml)
    return '<FullName>' in response


def create_customer(qb, name):
    """
    Create a customer in QuickBooks.
    
    Args:
        qb: Active SessionManager instance
        name: Customer name
        
    Returns:
        dict with success and message
    """
    if check_entity_exists(qb, "customer", name):
        return {'success': True, 'message': f"Customer '{name}' already exists", 'created': False}
    
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerAddRq>
      <CustomerAdd>
        <Name>{name}</Name>
        <CompanyName>{name}</CompanyName>
      </CustomerAdd>
    </CustomerAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
    
    response = qb.send_request(xml)
    
    if 'statusCode="0"' in response:
        return {'success': True, 'message': f"Created customer: {name}", 'created': True}
    else:
        # Extract error message
        error_match = re.search(r'statusMessage="([^"]+)"', response)
        error_msg = error_match.group(1) if error_match else "Unknown error"
        return {'success': False, 'message': f"Failed to create customer: {error_msg}", 'created': False}


def create_service_item(qb, name, description="", price=100.00):
    """
    Create a service item in QuickBooks.
    
    Args:
        qb: Active SessionManager instance
        name: Item name
        description: Item description
        price: Default price
        
    Returns:
        dict with success and message
    """
    if check_entity_exists(qb, "item", name):
        return {'success': True, 'message': f"Item '{name}' already exists", 'created': False}
    
    # Note: Account name might need to be adjusted based on actual QB chart of accounts
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemServiceAddRq>
      <ItemServiceAdd>
        <Name>{name}</Name>
        <SalesOrPurchase>
          <Desc>{description or name}</Desc>
          <Price>{price:.2f}</Price>
          <AccountRef>
            <FullName>Sales</FullName>
          </AccountRef>
        </SalesOrPurchase>
      </ItemServiceAdd>
    </ItemServiceAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
    
    response = qb.send_request(xml)
    
    if 'statusCode="0"' in response:
        return {'success': True, 'message': f"Created item: {name}", 'created': True}
    else:
        # Extract error message
        error_match = re.search(r'statusMessage="([^"]+)"', response)
        error_msg = error_match.group(1) if error_match else "Unknown error"
        return {'success': False, 'message': f"Failed to create item: {error_msg}", 'created': False}


def setup_sample_data():
    """
    Setup sample customers and items for testing.
    Creates Universal Cellular Customer and common phone models.
    
    Returns:
        dict with success, results for each entity, and summary
    """
    qb = SessionManager()
    results = []
    
    try:
        qb.open_connection()
        results.append("✓ Connected to QuickBooks")
        
        qb.begin_session()
        results.append("✓ Session started\n")
        
        # Create customer
        results.append("Creating customer...")
        customer_result = create_customer(qb, "Universal Cellular Customer")
        if customer_result['success']:
            results.append(f"  ✓ {customer_result['message']}")
        else:
            results.append(f"  ✗ {customer_result['message']}")
        
        # Create sample items
        results.append("\nCreating sample items...")
        sample_items = [
            ("APPLE-IPHONE XS-A1920", "iPhone XS 64GB", 250.00),
            ("APPLE-IPHONE 12", "iPhone 12 128GB", 400.00),
            ("SAMSUNG-GALAXY S21", "Galaxy S21", 350.00),
            ("TEST-DEVICE", "Test Device for Automation", 100.00),
        ]
        
        items_created = 0
        items_existed = 0
        items_failed = 0
        
        for item_name, desc, price in sample_items:
            item_result = create_service_item(qb, item_name, desc, price)
            if item_result['success']:
                if item_result['created']:
                    items_created += 1
                    results.append(f"  ✓ Created: {item_name}")
                else:
                    items_existed += 1
                    results.append(f"  ○ Already exists: {item_name}")
            else:
                items_failed += 1
                results.append(f"  ✗ Failed: {item_name} - {item_result['message']}")
        
        results.append(f"\nSummary: {items_created} created, {items_existed} already existed, {items_failed} failed")
        
        return {
            'success': items_failed == 0,
            'message': 'Sample data setup complete',
            'results': results
        }
        
    except Exception as e:
        results.append(f"\n✗ Error: {str(e)}")
        return {
            'success': False,
            'message': str(e),
            'results': results
        }
    finally:
        if qb.connection_open:
            qb.close_qb()
            results.append("\n✓ Connection closed")


def create_test_invoice():
    """
    Create a simple test invoice to verify write access.
    Uses the first available customer and item.
    
    Returns:
        dict with success, invoice details, and raw response
    """
    qb = SessionManager()
    steps = []
    
    try:
        qb.open_connection()
        steps.append("✓ Connected")
        
        qb.begin_session()
        steps.append("✓ Session started")
        
        # Find first customer
        steps.append("\nFinding customer...")
        cust_xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq><MaxReturned>1</MaxReturned></CustomerQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
        cust_response = qb.send_request(cust_xml)
        cust_match = re.search(r'<FullName>([^<]+)</FullName>', cust_response)
        
        if not cust_match:
            return {
                'success': False,
                'message': 'No customers found in QuickBooks. Run "Setup Sample Data" first.',
                'steps': steps
            }
        
        customer_name = cust_match.group(1)
        steps.append(f"  Using customer: {customer_name}")
        
        # Find first item
        steps.append("\nFinding item...")
        item_xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemQueryRq><MaxReturned>5</MaxReturned></ItemQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
        item_response = qb.send_request(item_xml)
        item_matches = re.findall(r'<FullName>([^<]+)</FullName>', item_response)
        
        if not item_matches:
            return {
                'success': False,
                'message': 'No items found in QuickBooks. Run "Setup Sample Data" first.',
                'steps': steps
            }
        
        item_name = item_matches[0]
        steps.append(f"  Using item: {item_name}")
        
        # Create invoice
        from datetime import date
        today = date.today().isoformat()
        
        steps.append(f"\nCreating invoice...")
        invoice_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>{customer_name}</FullName>
        </CustomerRef>
        <TxnDate>{today}</TxnDate>
        <Memo>AUTOMATION-TEST</Memo>
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{item_name}</FullName>
          </ItemRef>
          <Desc>Test line item from automation</Desc>
          <Quantity>1</Quantity>
          <Rate>10.00</Rate>
        </InvoiceLineAdd>
      </InvoiceAdd>
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
        
        response = qb.send_request(invoice_xml)
        
        if 'statusCode="0"' in response:
            # Extract invoice details
            txn_match = re.search(r'<TxnID>([^<]+)</TxnID>', response)
            ref_match = re.search(r'<RefNumber>([^<]+)</RefNumber>', response)
            
            txn_id = txn_match.group(1) if txn_match else "Unknown"
            ref_number = ref_match.group(1) if ref_match else "Unknown"
            
            steps.append(f"  ✓ Invoice #{ref_number} created!")
            steps.append(f"  TxnID: {txn_id}")
            
            return {
                'success': True,
                'message': f'Test invoice #{ref_number} created successfully!',
                'invoice': {
                    'ref_number': ref_number,
                    'txn_id': txn_id,
                    'customer': customer_name,
                    'item': item_name,
                    'date': today
                },
                'steps': steps
            }
        else:
            # Extract error
            error_match = re.search(r'statusMessage="([^"]+)"', response)
            error_msg = error_match.group(1) if error_match else "Unknown error"
            steps.append(f"  ✗ Error: {error_msg}")
            
            return {
                'success': False,
                'message': f'Failed to create invoice: {error_msg}',
                'steps': steps,
                'raw_response': response[:1000]
            }
        
    except Exception as e:
        steps.append(f"\n✗ Error: {str(e)}")
        return {
            'success': False,
            'message': str(e),
            'steps': steps
        }
    finally:
        if qb.connection_open:
            qb.close_qb()
            steps.append("\n✓ Connection closed")
