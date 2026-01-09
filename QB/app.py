"""
Flask server for Excel to Invoice generation.
Provides drag-and-drop upload interface and mock invoice generation.
"""
from flask import Flask, render_template, request, jsonify
import os

from excel_parser import parse_receiving_report
from invoice_generator import generate_mock_invoice

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
        
        # Generate mock invoice
        invoice_result = generate_mock_invoice(parsed_data)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(invoice_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
