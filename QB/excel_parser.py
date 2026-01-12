"""
Excel parser for Receiving Report format.
Parses the specific format used by Universal Cellular.
"""
import pandas as pd
from collections import defaultdict


def parse_receiving_report(filepath: str) -> dict:
    """
    Parse a Receiving Report Excel file.
    
    Expected columns:
    - PART NUMBER: Item identifier (e.g., "APPLE-IPHONE XS -A1920")
    - DESCRIPTION: Storage + Color (e.g., "64GB-SPACE GRAY")
    - IMEI: Unique device serial number
    - TYPE: Device type (e.g., "PHONE")
    - MAKE: Manufacturer (e.g., "APPLE")
    - MODEL: Model name (e.g., "IPHONE XS")
    - QTY: Quantity (only on first row of each group)
    - UC: Unit Cost
    - ORDER NUMBER: Reference (e.g., "INV: 50400")
    - DATE: Transaction date
    - RECEIVING REPORT NUMBER: RR number
    
    Returns:
        dict with invoice data structure
    """
    # Read Excel file
    df = pd.read_excel(filepath, header=0)
    
    # Normalize column names (strip whitespace, handle variations)
    df.columns = df.columns.str.strip()
    
    # Map common column name variations
    column_mapping = {
        'PART NUMBER': ['PART NUMBER', 'PARTNUMBER', 'PART_NUMBER', 'PART #'],
        'DESCRIPTION': ['DESCRIPTION', 'DESC'],
        'IMEI': ['IMEI', 'IMEI / SERIAL NUMBER', 'SERIAL NUMBER', 'SERIAL'],
        'QTY': ['QTY', 'QUANTITY'],
        'UC': ['UC', 'UNIT COST', 'UNIT_COST', 'RATE', 'PRICE'],
        'ORDER NUMBER': ['ORDER NUMBER', 'ORDER_NUMBER', 'ORDER #', 'ORDER'],
        'DATE': ['DATE', 'TXN DATE', 'TRANSACTION DATE'],
        'RECEIVING REPORT NUMBER': ['RECEIVING REPORT NUMBER', 'RR NUMBER', 'RR #', 'RR'],
        'MODEL': ['MODEL'],
        'MAKE': ['MAKE', 'MANUFACTURER'],
        'COLOR': ['COLOR'],
        'STORAGE': ['STORAGE'],
    }
    
    def find_column(df, possible_names):
        """Find the actual column name from possible variations."""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    # Find actual column names
    col_part = find_column(df, column_mapping['PART NUMBER'])
    col_desc = find_column(df, column_mapping['DESCRIPTION'])
    col_imei = find_column(df, column_mapping['IMEI'])
    col_qty = find_column(df, column_mapping['QTY'])
    col_uc = find_column(df, column_mapping['UC'])
    col_order = find_column(df, column_mapping['ORDER NUMBER'])
    col_date = find_column(df, column_mapping['DATE'])
    col_rr = find_column(df, column_mapping['RECEIVING REPORT NUMBER'])
    col_model = find_column(df, column_mapping['MODEL'])
    col_make = find_column(df, column_mapping['MAKE'])
    
    # Extract header info from first data row
    first_row = df.iloc[0] if len(df) > 0 else {}
    
    order_number = str(first_row.get(col_order, 'N/A')) if col_order else 'N/A'
    rr_number = str(first_row.get(col_rr, 'N/A')) if col_rr else 'N/A'
    raw_date = first_row.get(col_date) if col_date else None
    
    # Clean up RR number (might be float)
    try:
        rr_number = str(int(float(rr_number)))
    except (ValueError, TypeError):
        pass
    
    # Format date as YYYY-MM-DD for QuickBooks
    date = None
    if raw_date is not None and pd.notna(raw_date):
        try:
            if hasattr(raw_date, 'strftime'):
                # It's already a datetime object
                date = raw_date.strftime('%Y-%m-%d')
            else:
                # Try to parse it
                parsed = pd.to_datetime(raw_date)
                date = parsed.strftime('%Y-%m-%d')
        except:
            pass
    
    # Default to today if no valid date
    if not date:
        from datetime import date as dt_date
        date = dt_date.today().isoformat()
    
    # Group items by PART NUMBER + DESCRIPTION
    line_items = defaultdict(lambda: {
        'part_number': '',
        'description': '',
        'model': '',
        'make': '',
        'imeis': [],
        'quantity': 0,
        'unit_cost': 0,
        'amount': 0
    })
    
    total_imeis = 0
    
    for idx, row in df.iterrows():
        part_number = str(row.get(col_part, '')).strip() if col_part else ''
        description = str(row.get(col_desc, '')).strip() if col_desc else ''
        imei = str(row.get(col_imei, '')).strip() if col_imei else ''
        
        # Skip empty rows
        if not part_number or part_number == 'nan':
            continue
        
        # Create unique key for grouping
        key = f"{part_number}|{description}"
        
        item = line_items[key]
        item['part_number'] = part_number
        item['description'] = description
        
        if col_model:
            item['model'] = str(row.get(col_model, '')).strip()
        if col_make:
            item['make'] = str(row.get(col_make, '')).strip()
        
        # Get unit cost (should be same for all items in group)
        if col_uc and pd.notna(row.get(col_uc)):
            try:
                item['unit_cost'] = float(row.get(col_uc, 0))
            except (ValueError, TypeError):
                pass
        
        # Add IMEI to list
        if imei and imei != 'nan':
            item['imeis'].append(imei)
            total_imeis += 1
    
    # Calculate quantities and amounts
    items_list = []
    total_amount = 0
    
    for key, item in line_items.items():
        item['quantity'] = len(item['imeis'])
        item['amount'] = item['quantity'] * item['unit_cost']
        total_amount += item['amount']
        items_list.append(item)
    
    # Sort by part number
    items_list.sort(key=lambda x: x['part_number'])
    
    return {
        'header': {
            'order_number': order_number,
            'rr_number': rr_number,
            'date': date,
            'customer': 'Universal Cellular Customer',  # Default customer
        },
        'line_items': items_list,
        'summary': {
            'total_line_items': len(items_list),
            'total_imeis': total_imeis,
            'total_amount': total_amount
        }
    }
