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


def get_first_item(qb):
    """Query QB for the first available item."""
    xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemQueryRq><MaxReturned>1</MaxReturned></ItemQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    response = qb.send_request(xml)
    match = re.search(r'<FullName>([^<]+)</FullName>', response)
    return match.group(1) if match else None


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
        
        # Get existing item from QB (use as generic item for all lines)
        generic_item = get_first_item(qb)
        if not generic_item:
            raise Exception("No items found in QuickBooks. Please add an item first.")
        print(f"Using QB item: {generic_item}")
        
        # Build line items XML
        # Use the generic item for all lines, put part details in description
        lines_xml = ""
        for item in parsed_data['line_items']:
            # Put part number + description in the Desc field
            part_number = item['part_number']
            description = item['description']
            full_desc = escape_xml(f"{part_number} - {description}")
            quantity = int(item['quantity']) if item['quantity'] else 1
            rate = float(item['unit_cost']) if item['unit_cost'] else 0.00
            
            lines_xml += f"""
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{escape_xml(generic_item)}</FullName>
          </ItemRef>
          <Desc>{full_desc}</Desc>
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
