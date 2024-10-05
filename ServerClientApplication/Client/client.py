from flask import Flask, request, jsonify
from source import client_helper
import os
import csv
import pydoc

app = Flask(__name__)

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """
    Params:
      Application Name 
      Frequency of sampling
      Timeout for monitoring
      Server_URL
    Returns: 
      Return 200 if successful api call
    """

    print("Starting API CALL /start_monitoring---------------------------")
    data = request.get_json()
    command = data.get('command')  
    frequency = data.get('frequency')
    timeout = data.get('timeout')
    server_url = data.get('server_url')

    if not os.path.exists("power_consumption.csv") or os.path.getsize("power_consumption.csv") == 0:
        with open("power_consumption.csv", "w", newline="") as csvfile:
            pass  # Just opening in 'w' mode clears the file

        with open("power_consumption.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "power_consumption_w", "app_name"])

    monitor = client_helper.PowerConsumptionMonitor(command, frequency, timeout, server_url)
    
    monitor.start_monitoring()

    return jsonify({"message": "Monitoring started"}), 200


# pydoc.writedoc('client')
# pydoc.writedoc('source.client_helper')

if __name__ == "__main__":
 
    app.run(port=5000,debug=True,host='0.0.0.0')
          