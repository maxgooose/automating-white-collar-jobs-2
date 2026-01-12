"""
Flask server for Excel to Invoice generation.
Provides drag-and-drop upload interface and mock invoice generation.
Also includes a diagnostics page for testing QuickBooks connection.
"""
from flask import Flask, render_template, request, jsonify
import os
import sys
import time
from datetime import datetime

from excel_parser import parse_receiving_report
from invoice_generator import generate_mock_invoice

# Add parent directory to path for quickbooks_desktop imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Environment variable to toggle real QB vs mock mode
# Default to True since we're working with real QuickBooks Desktop
USE_REAL_QB = os.getenv('USE_REAL_QB', 'true').lower() == 'true'


# =============================================================================
# Main Invoice Generator Routes
# =============================================================================

@app.route('/')
def index():
    """Serve the main upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle Excel file upload and generate invoice."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Invalid file type. Please upload an Excel file (.xlsx or .xls)'}), 400
    
    try:
        # Save file temporarily
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Parse the Excel file
        parsed_data = parse_receiving_report(filepath)
        
        # Generate invoice (real QB or mock based on env var)
        if USE_REAL_QB:
            from invoice_generator_qb import create_qb_invoice
            invoice_result = create_qb_invoice(parsed_data)
        else:
            invoice_result = generate_mock_invoice(parsed_data)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(invoice_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Diagnostics Routes
# =============================================================================

@app.route('/diagnostics')
def diagnostics():
    """Serve the diagnostics/testing page."""
    return render_template('diagnostics.html')


@app.route('/test/connection', methods=['POST'])
def test_connection():
    """Test basic QuickBooks connection."""
    start_time = time.time()
    
    try:
        from quickbooks_desktop.qb_helpers import test_connection as qb_test_connection
        result = qb_test_connection()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Format output for display
        output_lines = result.get('steps', [])
        if result['success']:
            output_lines.append(f"\n✅ {result['message']}")
        else:
            output_lines.append(f"\n❌ {result['message']}")
        
        return jsonify({
            'success': result['success'],
            'output': '\n'.join(output_lines),
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat()
        })
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'output': f"❌ Import Error: {str(e)}\n\nMake sure you're running on Windows with pywin32 installed.",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f"❌ Error: {str(e)}",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/test/query-customers', methods=['POST'])
def test_query_customers():
    """Query customers from QuickBooks."""
    start_time = time.time()
    
    try:
        from quickbooks_desktop.qb_helpers import query_customers
        result = query_customers(max_returned=10)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Format output
        output_lines = []
        if result['success']:
            output_lines.append(f"✅ {result['message']}\n")
            output_lines.append("Customers found:")
            for i, cust in enumerate(result['customers'], 1):
                output_lines.append(f"  {i}. {cust}")
            if not result['customers']:
                output_lines.append("  (no customers in database)")
        else:
            output_lines.append(f"❌ {result['message']}")
        
        return jsonify({
            'success': result['success'],
            'output': '\n'.join(output_lines),
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat(),
            'data': result.get('customers', [])
        })
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'output': f"❌ Import Error: {str(e)}\n\nMake sure you're running on Windows with pywin32 installed.",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f"❌ Error: {str(e)}",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/test/query-invoices', methods=['POST'])
def test_query_invoices():
    """Query invoices from QuickBooks."""
    start_time = time.time()
    
    try:
        from quickbooks_desktop.qb_helpers import query_invoices
        result = query_invoices(max_returned=None)  # None = get all invoices
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Format output
        output_lines = []
        if result['success']:
            output_lines.append(f"✅ {result['message']}\n")
            output_lines.append("All invoices:")
            for inv in result['invoices']:
                output_lines.append(f"  #{inv['ref_number']} - {inv['date']} (TxnID: {inv['txn_id'][:10]}...)")
            if not result['invoices']:
                output_lines.append("  (no invoices in database)")
        else:
            output_lines.append(f"❌ {result['message']}")
        
        return jsonify({
            'success': result['success'],
            'output': '\n'.join(output_lines),
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat(),
            'data': result.get('invoices', [])
        })
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'output': f"❌ Import Error: {str(e)}\n\nMake sure you're running on Windows with pywin32 installed.",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f"❌ Error: {str(e)}",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/test/create-invoice', methods=['POST'])
def test_create_invoice():
    """Create a test invoice in QuickBooks."""
    start_time = time.time()
    
    try:
        from quickbooks_desktop.qb_helpers import create_test_invoice
        result = create_test_invoice()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Format output
        output_lines = result.get('steps', [])
        if result['success']:
            output_lines.append(f"\n✅ {result['message']}")
            if 'invoice' in result:
                inv = result['invoice']
                output_lines.append(f"\nInvoice Details:")
                output_lines.append(f"  Number: {inv['ref_number']}")
                output_lines.append(f"  Customer: {inv['customer']}")
                output_lines.append(f"  Item: {inv['item']}")
                output_lines.append(f"  Date: {inv['date']}")
        else:
            output_lines.append(f"\n❌ {result['message']}")
        
        return jsonify({
            'success': result['success'],
            'output': '\n'.join(output_lines),
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat(),
            'data': result.get('invoice')
        })
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'output': f"❌ Import Error: {str(e)}\n\nMake sure you're running on Windows with pywin32 installed.",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f"❌ Error: {str(e)}",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/test/setup-data', methods=['POST'])
def test_setup_data():
    """Setup sample data (customer and items) in QuickBooks."""
    start_time = time.time()
    
    try:
        from quickbooks_desktop.qb_helpers import setup_sample_data
        result = setup_sample_data()
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Format output
        output_lines = result.get('results', [])
        if result['success']:
            output_lines.append(f"\n✅ {result['message']}")
        else:
            output_lines.append(f"\n⚠️ {result['message']}")
        
        return jsonify({
            'success': result['success'],
            'output': '\n'.join(output_lines),
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat()
        })
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'output': f"❌ Import Error: {str(e)}\n\nMake sure you're running on Windows with pywin32 installed.",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f"❌ Error: {str(e)}",
            'duration_ms': int((time.time() - start_time) * 1000),
            'timestamp': datetime.now().isoformat()
        })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
