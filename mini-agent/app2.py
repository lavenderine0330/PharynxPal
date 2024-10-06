from flask import Flask, request, jsonify, send_file
from datetime import datetime
import csv
from io import StringIO
from io import BytesIO

app = Flask(__name__)

@app.route('/history', methods=['GET'])
def history():
    time_range = request.args.get('time_range')
    data_format = request.args.get('format')
    
    # Read the CSV file
    csv_file_path = '../detection_results.csv'
    rows = []
    
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)

    # Filter rows based on the requested time range (this is a simplified example)
    if time_range:
        start_time_str, end_time_str = time_range.split(',')
        #解析时间
        start_time = datetime.strptime(start_time_str.strip(), '%Y-%m-%d %H:%M') 
        end_time = datetime.strptime(end_time_str.strip(), '%Y-%m-%d %H:%M')
        rows = [row for row in rows if start_time <= datetime.strptime(row['time'], '%Y-%m-%d %H:%M') <= end_time]
    if not time_range:
        return "Missing 'time_range' parameter", 400
    if not rows:
        return "No data during this time_range"

    if data_format == 'csv':
        # Use StringIO to write CSV data as a string
        string_io = StringIO()
        writer = csv.DictWriter(string_io, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

        # Encode the CSV data to bytes
        output = BytesIO()
        output.write(string_io.getvalue().encode('utf-8'))
        output.seek(0)
        
        # Return CSV data as a file download
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='behavior_data.csv')
    elif data_format == 'json':
        # Return data as JSON
        return jsonify(rows)

    # If no format specified, return an error
    return "Format not supported", 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
