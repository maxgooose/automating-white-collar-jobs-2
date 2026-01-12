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

    # try: if connection fails, return error. if session fails, return error. if invoice fails, return error. if response is not 0, return error. i think i can type pretty fast now its not at a point where this is negotiable or debatable .i seke who i am and 
    
    try:
        # Connect to QuickBooks
        qb.open_connection()
        qb.begin_session()
        
        header = parsed_data['header']
        
        # Build line items XML
        # For each unique part number, we create one line item with quantity = number of IMEIs
        lines_xml = ""
        for item in parsed_data['line_items']:
            # Escape special characters in text fields
            part_number = escape_xml(item['part_number'])
            description = escape_xml(item['description'])
            
            lines_xml += f"""
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{part_number}</FullName>
          </ItemRef>
          <Desc>{description}</Desc>
          <Quantity>{item['quantity']}</Quantity>
          <Rate>{item['unit_cost']:.2f}</Rate>
        </InvoiceLineAdd>"""
        
        # Build full invoice XML
        customer = escape_xml(header['customer'])
        memo = escape_xml(f"RR# {header['rr_number']} - {header['order_number']}")
        
        invoice_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>{customer}</FullName>
        </CustomerRef>
        <TxnDate>{header['date']}</TxnDate>
        <Memo>{memo}</Memo>
        {lines_xml}
      </InvoiceAdd>
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
        
        # Send request to QuickBooks
        response = qb.send_request(invoice_xml)
        
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
                    'customer': header['customer'],
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
