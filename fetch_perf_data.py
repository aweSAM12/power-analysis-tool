from flask import Flask, request, jsonify
import csv
from datetime import datetime, timedelta

app = Flask(__name__)

PERF_LOG_FILE = 'power_consumption.csv'  # Update with the file created by the perf script

def query_power_data(start_time):
    power_data = []
    with open(PERF_LOG_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            if timestamp >= start_time:
                power_data.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'power_consumption_w': float(row['power_consumption_w'])
                })
    return power_data

def parse_frequency(frequency):
    now = datetime.now()
    if frequency.endswith('m'):
        minutes = int(frequency[:-1])
        return now - timedelta(minutes=minutes)
    elif frequency.endswith('h'):
        hours = int(frequency[:-1])
        return now - timedelta(hours=hours)
    elif frequency.endswith('d'):
        days = int(frequency[:-1])
        return now - timedelta(days=days)
    else:
        raise ValueError("Invalid frequency format. Use '10m', '1h', or '1d'.")

@app.route('/power', methods=['GET'])
def get_power():
    frequency = request.args.get('frequency', default='1h', type=str)
    
    try:
        start_time = parse_frequency(frequency)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    power_data = query_power_data(start_time)
    
    if not power_data:
        return jsonify({'error': 'No data available for the specified time range'}), 404

    return jsonify({'data': power_data, 'frequency': frequency})

if __name__ == '__main__':
    app.run(debug=True)



# def query_power_data(start_time):
#     total_power_consumed = 0.0
#     with open(PERF_LOG_FILE, 'r') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
#             if timestamp >= start_time:
#                 total_power_consumed += float(row['power_consumption_w'])
#             # Debug information
#             print(f"Checking row: Timestamp={timestamp}, Power={row['power_consumption_w']} , {start_time}")
#             print(f"Row included: {timestamp >= start_time}")
#     return total_power_consumed

# def parse_frequency(frequency):
#     now = datetime.now()
#     if frequency.endswith('m'):
#         minutes = int(frequency[:-1])
#         return now - timedelta(minutes=minutes)
#     elif frequency.endswith('h'):
#         hours = int(frequency[:-1])
#         return now - timedelta(hours=hours)
#     elif frequency.endswith('d'):
#         days = int(frequency[:-1])
#         return now - timedelta(days=days)
#     else:
#         raise ValueError("Invalid frequency format. Use '10m', '1h', or '1d'.")

# @app.route('/power', methods=['GET'])
# def get_power():
#     frequency = request.args.get('frequency', default='1h', type=str)
    
#     try:
#         start_time = parse_frequency(frequency)
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
    
#     total_power_consumed = query_power_data(start_time)
    
#     if total_power_consumed == 0.0:
#         return jsonify({'error': 'No data available for the specified time range'}), 404

#     return jsonify({'total_power_consumed_w': total_power_consumed, 'frequency': frequency})

# if __name__ == '__main__':
#     app.run(debug=True)

