"""
Real QuickBooks invoice generator.
Connects to QB Desktop and creates actual invoices.
"""
import re
import sys
import os
from datetime import datetime

# Add parent directory to path for quickbooks_desktop imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quickbooks_desktop.session_manager import SessionManager


def escape_xml(text):
    """
    Escape special characters for XML.
    
    Args:
        text: String to escape
        
    Returns:
        XML-safe string
    """
    if not isinstance(text, str):
        text = str(text)
    
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text


def get_first_customer(qb):
    """Query QB for the first available customer."""
    xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <CustomerQueryRq><MaxReturned>1</MaxReturned></CustomerQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    response = qb.send_request(xml)
    match = re.search(r'<FullName>([^<]+)</FullName>', response)
    return match.group(1) if match else None


def item_exists(qb, item_name):
    """Check if an item exists in QuickBooks."""
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemQueryRq>
      <FullName>{escape_xml(item_name)}</FullName>
    </ItemQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    response = qb.send_request(xml)
    return 'statusCode="0"' in response and '<FullName>' in response


def create_service_item(qb, item_name, description="", price=0.00):
    """Create a service item in QuickBooks if it doesn't exist."""
    if item_exists(qb, item_name):
        print(f"  Item already exists: {item_name}")
        return True
    
    print(f"  Creating item: {item_name}")
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemServiceAddRq>
      <ItemServiceAdd>
        <Name>{escape_xml(item_name[:31])}</Name>
        <SalesOrPurchase>
          <Desc>{escape_xml(description or item_name)}</Desc>
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
        print(f"    ✓ Created successfully")
        return True
    else:
        # Extract error
        error_match = re.search(r'statusMessage="([^"]+)"', response)
        error_msg = error_match.group(1) if error_match else "Unknown error"
        print(f"    ✗ Failed: {error_msg}")
        return False


def create_qb_invoice(parsed_data: dict) -> dict:
    """
    Create a real invoice in QuickBooks from parsed Excel data.
    
    Args:
        parsed_data: Output from excel_parser.parse_receiving_report()
        
    Returns:
        dict with invoice result and QB response (same format as mock generator)

    Example: 
        parsed data -> excel parser -> parsed_data -> invoice generator -> invoice xml -> send to qb -> response -> return to app.py
    """
    qb = SessionManager()
    
    try:
        # Connect to QuickBooks
        qb.open_connection()
        qb.begin_session()
        
        header = parsed_data['header']
        
        # Get existing customer from QB (like the test invoice does)
        customer = get_first_customer(qb)
        if not customer:
            raise Exception("No customers found in QuickBooks. Please add a customer first.")
        print(f"Using QB customer: {customer}")
        
        # Step 1: Collect unique item names and ensure they exist in QB
        print("\n--- Validating/Creating Items in QuickBooks ---")
        unique_items = set()
        for item in parsed_data['line_items']:
            unique_items.add(item['part_number'])
        
        print(f"Found {len(unique_items)} unique items to validate")
        
        items_created = 0
        items_existed = 0
        items_failed = 0
        
        for item_name in unique_items:
            # Try to create item (will skip if exists)
            if item_exists(qb, item_name):
                items_existed += 1
                print(f"  ✓ Exists: {item_name}")
            else:
                if create_service_item(qb, item_name, item_name, 0.00):
                    items_created += 1
                else:
                    items_failed += 1
        
        print(f"\nItem summary: {items_existed} existed, {items_created} created, {items_failed} failed")
        
        if items_failed > 0:
            raise Exception(f"Failed to create {items_failed} items in QuickBooks")
        
        # Step 2: Build line items XML using actual part numbers
        print("\n--- Building Invoice XML ---")
        lines_xml = ""
        for item in parsed_data['line_items']:
            part_number = item['part_number']
            description = item['description']
            quantity = int(item['quantity']) if item['quantity'] else 1
            rate = float(item['unit_cost']) if item['unit_cost'] else 0.00
            
            lines_xml += f"""
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{escape_xml(part_number)}</FullName>
          </ItemRef>
          <Desc>{escape_xml(description)}</Desc>
          <Quantity>{quantity}</Quantity>
          <Rate>{rate:.2f}</Rate>
        </InvoiceLineAdd>"""
        
        # Build full invoice XML
        memo = escape_xml(f"RR# {header['rr_number']} - {header['order_number']}")
        txn_date = header['date']
        
        # Validate date format (must be YYYY-MM-DD)
        if not txn_date or len(txn_date) != 10 or txn_date[4] != '-' or txn_date[7] != '-':
            from datetime import date
            txn_date = date.today().isoformat()
        
        invoice_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>{escape_xml(customer)}</FullName>
        </CustomerRef>
        <TxnDate>{txn_date}</TxnDate>
        <Memo>{memo}</Memo>{lines_xml}
      </InvoiceAdd>
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
        
        # Debug: print the XML being sent (can be removed later)
        print("=" * 50)
        print("INVOICE XML BEING SENT TO QB:")
        print("=" * 50)
        print(invoice_xml)
        print("=" * 50)
        
        # Send request to QuickBooks
        response = qb.send_request(invoice_xml)
        
        # Debug: print QB response
        print("=" * 50)
        print("QUICKBOOKS RESPONSE:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
        # Parse response
        if 'statusCode="0"' in response:
            # Success - extract invoice details
            txn_match = re.search(r'<TxnID>([^<]+)</TxnID>', response)
            ref_match = re.search(r'<RefNumber>([^<]+)</RefNumber>', response)
            
            txn_id = txn_match.group(1) if txn_match else "Unknown"
            invoice_number = ref_match.group(1) if ref_match else "Unknown"
            
            # Build QB-style line items for response
            qb_line_items = []
            for idx, item in enumerate(parsed_data['line_items'], 1):
                qb_line_items.append({
                    'line_number': idx,
                    'item_ref': item['part_number'],
                    'description': f"{item['description']} ({item['make']} {item['model']})" if item.get('make') else item['description'],
                    'quantity': item['quantity'],
                    'rate': item['unit_cost'],
                    'amount': item['amount'],
                    'serial_numbers': item['imeis'][:5] + (['...'] if len(item['imeis']) > 5 else []),
                    'total_serials': len(item['imeis'])
                })
            
            return {
                'success': True,
                'message': f'Invoice {invoice_number} created in QuickBooks',
                'invoice': {
                    'number': invoice_number,
                    'txn_id': txn_id,
                    'customer': customer,  # Actual QB customer used
                    'date': header['date'],
                    'memo': f"RR# {header['rr_number']} - {header['order_number']}",
                    'line_items': qb_line_items,
                    'summary': {
                        'line_count': len(qb_line_items),
                        'total_units': parsed_data['summary']['total_imeis'],
                        'subtotal': parsed_data['summary']['total_amount'],
                        'total': parsed_data['summary']['total_amount']
                    }
                },
                'qb_response': {
                    'status_code': 0,
                    'status_message': 'Status OK',
                    'txn_id': txn_id,
                    'ref_number': invoice_number
                },
                'demo_mode': False,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Error - extract error message
            error_match = re.search(r'statusMessage="([^"]+)"', response)
            error_msg = error_match.group(1) if error_match else "Unknown QuickBooks error"
            
            # Extract status code
            code_match = re.search(r'statusCode="([^"]+)"', response)
            status_code = code_match.group(1) if code_match else "Unknown"
            
            raise Exception(f"QuickBooks error ({status_code}): {error_msg}")

                        
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Failed to create invoice: {str(e)}',
            'invoice': None,
            'demo_mode': False,
            'timestamp': datetime.now().isoformat()
        }
        
    finally:
        if qb.session_begun:
            qb.end_session()
        if qb.connection_open:
            qb.close_connection()
