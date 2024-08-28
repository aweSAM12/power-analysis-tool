from flask import Flask, request, jsonify
import csv
from datetime import datetime, timedelta

app = Flask(__name__)

LOG_FILE = 'powertop_output.csv'

def query_pid_data(pid, start_time):
    total_power_consumed = 0.0
    with open(LOG_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            if int(row['pid']) == pid and timestamp >= start_time:
                total_power_consumed += float(row['power_consumption_w'])
            # Debug information
            print(f"Checking row: PID={row['pid']}, Timestamp={timestamp}, Power={row['power_consumption_w']} , {start_time}")
            print(f"Row included: {int(row['pid']) == pid and timestamp >= start_time}")
    return total_power_consumed

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
        raise ValueError("Invalid frequency format. Use '10m', '1h, or '1d'.")

@app.route('/power', methods=['GET'])
def get_power():
    pid = request.args.get('pid', type=int)
    frequency = request.args.get('frequency', default='1h', type=str)
    
    if pid is None:
        return jsonify({'error': 'Missing required parameter: pid'}), 400
    
    try:
        start_time = parse_frequency(frequency)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    total_power_consumed = query_pid_data(pid, start_time)
    
    if total_power_consumed == 0.0:
        return jsonify({'error': 'PID not found or no data available for the specified time range'}), 404

    return jsonify({'pid': pid, 'total_power_consumed_w': total_power_consumed, 'frequency': frequency})

if __name__ == '__main__':
    app.run(debug=True)
