"""
Invoice generator with mock QuickBooks response.
For demo purposes - simulates QB invoice creation.
"""
import random
import string
from datetime import datetime


def generate_mock_invoice(parsed_data: dict) -> dict:
    """
    Generate a mock QuickBooks invoice response.
    
    In production, this would connect to QuickBooks Desktop
    using the SessionManager and create a real invoice.
    
    For the demo, we simulate a successful invoice creation.
    
    Args:
        parsed_data: Output from excel_parser.parse_receiving_report()
    
    Returns:
        dict with invoice result and mock QB response
    """
    # Generate mock invoice number
    invoice_number = f"INV-{random.randint(10000, 99999)}"
    txn_id = f"TXN-{random.randint(100000, 999999)}"
    
    # Build QB-style line items
    qb_line_items = []
    for idx, item in enumerate(parsed_data['line_items'], 1):
        qb_line_items.append({
            'line_number': idx,
            'item_ref': item['part_number'],
            'description': f"{item['description']} ({item['make']} {item['model']})" if item.get('make') else item['description'],
            'quantity': item['quantity'],
            'rate': item['unit_cost'],
            'amount': item['amount'],
            'serial_numbers': item['imeis'][:5] + (['...'] if len(item['imeis']) > 5 else []),  # Show first 5
            'total_serials': len(item['imeis'])
        })
    
    # Build mock QB response
    mock_qb_response = {
        'status_code': 0,
        'status_message': 'Status OK',
        'invoice_ret': {
            'txn_id': txn_id,
            'txn_number': invoice_number,
            'customer_ref': {
                'full_name': parsed_data['header']['customer']
            },
            'txn_date': parsed_data['header']['date'],
            'due_date': parsed_data['header']['date'],
            'memo': f"RR# {parsed_data['header']['rr_number']} - {parsed_data['header']['order_number']}",
            'subtotal': parsed_data['summary']['total_amount'],
            'total_amount': parsed_data['summary']['total_amount'],
            'is_paid': False
        }
    }
    
    return {
        'success': True,
        'message': f'Invoice {invoice_number} created successfully',
        'invoice': {
            'number': invoice_number,
            'txn_id': txn_id,
            'customer': parsed_data['header']['customer'],
            'date': parsed_data['header']['date'],
            'memo': f"RR# {parsed_data['header']['rr_number']} - {parsed_data['header']['order_number']}",
            'line_items': qb_line_items,
            'summary': {
                'line_count': len(qb_line_items),
                'total_units': parsed_data['summary']['total_imeis'],
                'subtotal': parsed_data['summary']['total_amount'],
                'total': parsed_data['summary']['total_amount']
            }
        },
        'qb_response': mock_qb_response,
        'demo_mode': True,
        'timestamp': datetime.now().isoformat()
    }


def generate_qbxml_invoice(parsed_data: dict) -> str:
    """
    Generate qbXML for invoice creation.
    This is what would be sent to QuickBooks in production.
    
    Returns the XML string that would be sent via SessionManager.
    """
    header = parsed_data['header']
    
    # Build line items XML
    lines_xml = ""
    for item in parsed_data['line_items']:
        # For each unique item, create a line
        lines_xml += f"""
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{item['part_number']}</FullName>
          </ItemRef>
          <Desc>{item['description']}</Desc>
          <Quantity>{item['quantity']}</Quantity>
          <Rate>{item['unit_cost']:.2f}</Rate>
        </InvoiceLineAdd>"""
    
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <InvoiceAddRq>
      <InvoiceAdd>
        <CustomerRef>
          <FullName>{header['customer']}</FullName>
        </CustomerRef>
        <TxnDate>{header['date']}</TxnDate>
        <Memo>RR# {header['rr_number']} - {header['order_number']}</Memo>
        {lines_xml}
      </InvoiceAdd>
    </InvoiceAddRq>
  </QBXMLMsgsRq>
</QBXML>"""
    
    return xml
