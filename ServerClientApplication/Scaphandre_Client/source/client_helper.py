import os
import csv
import subprocess
import threading
import logging
import requests
from datetime import datetime

class PowerConsumptionMonitor:
    CLIENT_NAME = "Client123"  # Hardcoded client name

    def __init__(self, command, frequency, timeout, server_url):
        self.command = command  # Command to execute for power monitoring
        self.frequency = frequency  # Frequency of monitoring in milliseconds
        self.timeout = timeout  # Timeout for monitoring in seconds
        self.server_url = server_url  # Server URL for uploading CSV
        self.app_name = self.extract_app_name(command)  # Extract application name from command
        self.setup_logging()  # Set up logging
        self.clear_csv()  # Clear CSV at the start

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)  # Initialize logger

    def clear_csv(self):
        with open("power_consumption.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp","power_consumption_w","app_name"])  # Write headers

    def write_to_csv(self, timestamp, total_power_consumption_w):
        with open("power_consumption.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Ensure values are written in the exact order needed
            # writer.writerow([timestamp, total_power_consumption_w, self.app_name, self.CLIENT_NAME])
            writer.writerow([timestamp, total_power_consumption_w, self.app_name])
        self.logger.info(f"Written to CSV: {timestamp}, {total_power_consumption_w}, {self.app_name}")

    def extract_app_name(self, command):
        return os.path.basename(command.split()[1])  # Extract application name from command

    def start_scaphandre_monitoring(self):
        # Using Scaphandre command with "-p 10" to get top 10 consumers
        perf_command = [
            "sudo", "scaphandre", "--vm", "stdout", "-s", str(int(self.frequency / 1000)),
            "-t", str(self.timeout), "-p", "10"
        ]
        self.logger.info(f"Executing command: {' '.join(perf_command)}")

        process = subprocess.Popen(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def parse_scaphandre_output(pipe):
            power_values = []
            for line in iter(pipe.readline, ''):
                line = line.strip()
                self.logger.debug(f"Raw line: {line}")

                if line.startswith("Top 10 consumers:"):
                    power_values.clear()  # Reset power values for each new "Top 10 consumers" section

                # Try parsing the power value from lines with power consumption
                try:
                    if "W" in line and len(line.split()) > 2:
                        power_value_str = line.split()[0].replace("W", "")
                        power_watts = round(float(power_value_str), 2)
                        power_values.append(power_watts)
                        self.logger.debug(f"Parsed power value: {power_watts}")
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Failed to parse power from line: {line} with error: {e}")

                # If we have collected 10 values, calculate the sum and write to CSV
                if len(power_values) == 10:
                    total_power_consumption_w = round(sum(power_values), 2)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.write_to_csv(timestamp, total_power_consumption_w)
                    power_values.clear()  # Clear for the next set of data

            pipe.close()

        # Start threads for reading stdout and stderr
        stdout_thread = threading.Thread(target=parse_scaphandre_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=parse_scaphandre_output, args=(process.stderr,))
        
        stdout_thread.start()
        stderr_thread.start()

        def stop_process():
            process.terminate()  # Terminate the subprocess
            stdout_thread.join()  # Wait for stdout thread to finish
            stderr_thread.join()  # Wait for stderr thread to finish
            self.logger.info("Process terminated and threads joined.")
            self.upload_csv()  # Upload CSV after process completion

        timer = threading.Timer(self.timeout, stop_process)  # Schedule process stop
        timer.start()

        process.wait()  # Wait for process to complete
        stdout_thread.join()
        stderr_thread.join()

    def upload_csv(self):
        with open("power_consumption.csv", "rb") as f:
            files = {'file': f}
            data = {'client_name': self.CLIENT_NAME}  # Include client name in request
            response = requests.post(self.server_url, files=files, data=data)  # Upload CSV to server
            self.logger.info(f"CSV uploaded with response: {response.status_code}, {response.text}")