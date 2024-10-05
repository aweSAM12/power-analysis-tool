from flask import Flask, request, jsonify, render_template
import requests
import json
from source.server_helper import CSVHandler

app = Flask(__name__)
csv_handler = CSVHandler()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    command = request.form['command']
    frequency = int(request.form['frequency']) *1000
    timeout = request.form['timeout']
    server_url = request.form['server_url'] + '/upload_csv'
    client_url = request.form['client_url'] + '/start_monitoring'
    
    client_data = {
        "command": command,
        "frequency": frequency,
        "timeout": int(timeout),
        "server_url": server_url
    }
    
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(client_data)
    
    response = requests.post(client_url, headers=headers, data=json_data)
    
    return jsonify(response.json()), response.status_code


@app.route('/trigger_monitoring', methods=['POST'])
def trigger_monitoring():
    data = request.get_json()
    client_url = data.get('client_url')
    command = data.get('command')
    frequency = data.get('frequency')
    timeout = data.get('timeout')
    server_url = request.url_root + 'upload_csv'
    
    client_data = {
        "command": command,
        "frequency": frequency,
        "timeout": timeout,
        "server_url": server_url
    }
    
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(client_data)
    
    response = requests.post(client_url, headers=headers, data=json_data)
    
    return jsonify(response.json()), response.status_code

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    client_name = request.form['client_name']
    return csv_handler.upload_csv(file, client_name)

@app.route('/get_data', methods=['GET'])
def get_data():
    csv_files = csv_handler.get_data()
    return jsonify(csv_files)

@app.route('/power', methods=['GET'])
def get_power():
    frequency = request.args.get('frequency', default='1h', type=str)
    app_name = request.args.get('app_name', type=str)
    client_name = request.args.get('client_name', type=str)
    
    if not app_name or not client_name:
        return jsonify({'error': 'app_name and client_name parameters are required'}), 400
    
    try:
        start_time = csv_handler.parse_frequency(frequency)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    power_data = csv_handler.query_power_data(start_time, app_name, client_name)
    
    if not power_data:
        return jsonify({'error': 'No data available for the specified time range, app_name, and client_name'}), 404

    formatted_data = {}
    for hour in sorted(power_data.keys()):
        formatted_data[f'last {hour + 1} hrs'] = power_data[hour]
    
    return jsonify({'data': formatted_data, 'frequency': frequency, 'app_name': app_name, 'client_name': client_name})
    

@app.route('/plot')
def plot():
    return render_template('plot.html')

if __name__ == "__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')
