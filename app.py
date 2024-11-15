from flask import Flask, request, jsonify, send_from_directory
import json
from datetime import datetime
import os

app = Flask(__name__)

# Ensure the sales directory exists
if not os.path.exists('sales'):
    os.makedirs('sales')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/save_bill', methods=['POST'])
def save_bill():
    try:
        bill_data = request.json
        
        # Create a filename with timestamp
        filename = f"sales/bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save the bill data to a JSON file
        with open(filename, 'w') as f:
            json.dump(bill_data, f, indent=4)
        
        # Update daily sales summary
        today = datetime.now().strftime('%Y%m%d')
        summary_file = f"sales/summary_{today}.json"
        
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                daily_summary = json.load(f)
        else:
            daily_summary = {
                'total_sales': 0,
                'total_bills': 0,
                'items_sold': {}
            }
        
        # Update summary
        daily_summary['total_sales'] += bill_data['total']
        daily_summary['total_bills'] += 1
        
        # Update items sold
        for item_id, details in bill_data['items'].items():
            if details['name'] not in daily_summary['items_sold']:
                daily_summary['items_sold'][details['name']] = {
                    'quantity': 0,
                    'revenue': 0
                }
            daily_summary['items_sold'][details['name']]['quantity'] += details['quantity']
            daily_summary['items_sold'][details['name']]['revenue'] += details['quantity'] * details['price']
        
        # Save updated summary
        with open(summary_file, 'w') as f:
            json.dump(daily_summary, f, indent=4)
        
        return jsonify({'status': 'success', 'message': 'Bill saved successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)