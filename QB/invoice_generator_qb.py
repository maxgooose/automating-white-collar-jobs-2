"""
Real QuickBooks invoice generator.
Connects to QB Desktop and creates actual invoices.
"""
import re
import sys
import os
from datetime import datetime
import traceback

# CRITICAL: Set COM threading model BEFORE importing pythoncom
# 0 = COINIT_MULTITHREADED (required for Flask/web apps)
sys.coinit_flags = 0
import pythoncom

# Add parent directory to path for quickbooks_desktop imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quickbooks_desktop.session_manager import SessionManager


def escape_xml(text):
    """
    Escape special characters for XML and remove invalid XML characters.
    
    Args:
        text: String to escape
        
    Returns:
        XML-safe string
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters that are invalid in XML (except tab, newline, carriage return)
    # Valid XML chars: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD]
    cleaned = []
    for char in text:
        code = ord(char)
        if code == 0x9 or code == 0xA or code == 0xD:  # tab, newline, carriage return
            cleaned.append(char)
        elif code >= 0x20 and code <= 0xD7FF:
            cleaned.append(char)
        elif code >= 0xE000 and code <= 0xFFFD:
            cleaned.append(char)
        # else: skip invalid characters
    
    text = ''.join(cleaned)
    
    # Escape XML special characters (order matters - & must be first!)
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


def get_first_item(qb):
    """Query QB for the first available item (matching create_test_invoice pattern)."""
    xml = """<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="13.0"?>
<QBXML>
  <QBXMLMsgsRq onError="stopOnError">
    <ItemQueryRq><MaxReturned>5</MaxReturned></ItemQueryRq>
  </QBXMLMsgsRq>
</QBXML>"""
    response = qb.send_request(xml)
    # Find item names
    matches = re.findall(r'<FullName>([^<]+)</FullName>', response)
    return matches[0] if matches else None


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
    # Ensure COM is initialized for THIS thread (Flask may use different threads)
    # This is critical - COM objects are thread-specific and will crash if accessed from wrong thread
    print("\n" + "=" * 60)
    print("CREATE_QB_INVOICE STARTING")
    print("=" * 60)
    
    try:
        pythoncom.CoInitialize()
        print("✓ COM initialized")
    except Exception as e:
        print(f"COM init error (may be ok if already initialized): {e}")
    
    qb = SessionManager()
    
    try:
        # Connect to QuickBooks
        print("\n--- Step 1: Connecting to QuickBooks ---")
        try:
            qb.open_connection()
            print("✓ Connection opened")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            raise
        
        try:
            qb.begin_session()
            print("✓ Session started")
        except Exception as e:
            print(f"✗ Session failed: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            raise
        
        header = parsed_data['header']
        
        # Get existing customer from QB (same as create_test_invoice)
        print("\n--- Step 2: Finding Customer ---")
        try:
            customer = get_first_customer(qb)
            if not customer:
                raise Exception("No customers found in QuickBooks. Please add a customer first.")
            print(f"✓ Using QB customer: {customer}")
        except Exception as e:
            print(f"✗ Customer query failed: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            raise
        
        # Get existing item from QB (same as create_test_invoice - use what already exists!)
        print("\n--- Step 3: Finding Item ---")
        try:
            qb_item = get_first_item(qb)
            if not qb_item:
                raise Exception("No items found in QuickBooks. Run 'Setup Sample Data' first.")
            print(f"✓ Using QB item: {qb_item}")
        except Exception as e:
            print(f"✗ Item query failed: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            raise
        
        # Build line items XML - use the EXISTING QB item, put part details in description
        print(f"\n--- Step 4: Building Invoice XML ({len(parsed_data['line_items'])} line items) ---")
        lines_xml = ""
        for idx, item in enumerate(parsed_data['line_items'], 1):
            part_number = escape_xml(str(item.get('part_number', '') or ''))
            description = escape_xml(str(item.get('description', '') or ''))
            
            # Put full part number + description in the Desc field (limit to 4095 chars - QB max)
            full_desc = f"{part_number} | {description}"
            if len(full_desc) > 4095:
                full_desc = full_desc[:4092] + "..."
            
            # Ensure quantity is a valid integer
            try:
                quantity = int(item.get('quantity', 1) or 1)
                if quantity < 1:
                    quantity = 1
            except (ValueError, TypeError):
                quantity = 1
            
            # Ensure rate is a valid float
            try:
                rate = float(item.get('unit_cost', 0) or 0)
            except (ValueError, TypeError):
                rate = 0.00
            
            print(f"  Line {idx}: qty={quantity}, rate={rate:.2f}, desc={full_desc[:50]}...")
            
            lines_xml += f"""
        <InvoiceLineAdd>
          <ItemRef>
            <FullName>{escape_xml(qb_item)}</FullName>
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
        
        # Debug: print the FULL XML being sent (so we can see what breaks)
        print("\n--- Step 5: Sending Invoice to QuickBooks ---")
        print("FULL INVOICE XML:")
        print("=" * 40)
        print(invoice_xml)
        print("=" * 40)
        
        # Send request to QuickBooks
        try:
            response = qb.send_request(invoice_xml)
            print("✓ Request sent successfully")
        except Exception as e:
            print(f"✗ Request failed: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            raise
        
        # Debug: print QB response
        print("\nQUICKBOOKS RESPONSE:")
        print(response[:1000] if len(response) > 1000 else response)
        
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
        # Clean up in reverse order: session -> connection -> COM
        print("\n--- Cleanup ---")
        try:
            if qb.session_begun:
                qb.end_session()
                print("✓ Session ended")
        except Exception as e:
            print(f"⚠ Session end error: {e}")
        
        try:
            if qb.connection_open:
                qb.close_connection()
                print("✓ Connection closed")
        except Exception as e:
            print(f"⚠ Connection close error: {e}")
        
        # Release the COM object reference explicitly
        try:
            qb.qbXMLRP = None
            print("✓ COM object released")
        except:
            pass
        
        try:
            pythoncom.CoUninitialize()
            print("✓ COM uninitialized")
        except Exception as e:
            print(f"⚠ COM uninit error (may be ok): {e}")
        
        print("=" * 60)
        print("CREATE_QB_INVOICE FINISHED")
        print("=" * 60 + "\n")
