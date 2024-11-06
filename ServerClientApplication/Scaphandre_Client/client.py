from flask import Flask, request, jsonify
from source import client_helper
import os
import csv

app = Flask(__name__)

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """
    Params:
      command: The command to execute
      frequency: Frequency of sampling
      timeout: Timeout for monitoring
      server_url: URL to upload the CSV
    Returns: 
      200 status if the API call is successful
    """
    print("Starting API CALL /start_monitoring---------------------------")
    data = request.get_json()
    command = data.get('command')  
    frequency = data.get('frequency')
    timeout = data.get('timeout')
    server_url = data.get('server_url')

    # Create or initialize the CSV file if not exists
    if not os.path.exists("power_consumption.csv") or os.path.getsize("power_consumption.csv") == 0:
        with open("power_consumption.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "power_consumption_w", "app_name"])  # Initialize CSV with headers

    monitor = client_helper.PowerConsumptionMonitor(command, frequency, timeout, server_url)
    
    # Call start_scaphandre_monitoring for Scaphandre monitoring
    monitor.start_scaphandre_monitoring()

    return jsonify({"message": "Monitoring Finished Successfully"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')
