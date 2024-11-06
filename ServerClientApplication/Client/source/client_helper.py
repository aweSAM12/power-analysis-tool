import os
import csv
import subprocess
import threading
import logging
import requests
from datetime import datetime
import pydoc

class PowerConsumptionMonitor:
    CLIENT_NAME = "Client123"  # Hardcoded client name

    def __init__(self, command, frequency, timeout, server_url):
        self.command = command
        self.frequency = frequency
        self.timeout = timeout
        self.server_url = server_url
        self.app_name = self.extract_app_name(command)
        self.setup_logging()
        # self.clear_csv()

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def parse_perf_output(self, line):
        if "Joules power/energy-pkg/" in line:
            energy_joules = round(float(line.split()[1].replace(",", "")), 2)
            power_watts = round(energy_joules / (int(self.frequency) / 1000), 2)
            return power_watts
        return None
    
    def clear_csv(self):
        # Clear the file by opening it in write mode
        with open("power_consumption.csv", "w", newline="") as csvfile:
            pass  # Just opening in 'w' mode clears the file

    def write_to_csv(self, timestamp, power_consumption_w):
        with open("power_consumption.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, power_consumption_w, self.app_name])
        self.logger.info(f"Written to CSV: {timestamp}, {power_consumption_w}, {self.app_name}")

    def read_output(self, pipe):
        for line in iter(pipe.readline, ''):
            line = line.strip()
            self.logger.debug(f"Raw line: {line}")
            power_consumption_w = self.parse_perf_output(line)
            # self.clear_csv()
            if power_consumption_w is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.logger.debug(f"Parsed power (W): {power_consumption_w}")
                self.write_to_csv(timestamp, power_consumption_w)
        pipe.close()

    def extract_app_name(self, command):
        return os.path.basename(command.split()[1])

    def start_monitoring(self):
        perf_command = ["sudo", "perf", "stat", "-e", "power/energy-pkg/", "-I", str(self.frequency) , 'sleep' , str(self.timeout)] # + self.command.split()
        self.logger.info(f"Executing command: {' '.join(perf_command)}")
        process = subprocess.Popen(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout_thread = threading.Thread(target=self.read_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=self.read_output, args=(process.stderr,))

        stdout_thread.start()
        stderr_thread.start()

        def stop_process():
            process.terminate()
            stdout_thread.join()
            stderr_thread.join()
            self.logger.info("Process terminated and threads joined.")
            self.upload_csv()

        timer = threading.Timer(self.timeout, stop_process)
        timer.start()

        process.wait()
        stdout_thread.join()
        stderr_thread.join()
    
    def upload_csv(self):
        print("Uploading CSV ---------------------------------")
        with open("power_consumption.csv", "rb") as f:
            files = {'file': f}
            data = {'client_name': self.CLIENT_NAME}
            response = requests.post(self.server_url, files=files, data=data)
            self.logger.info(f"CSV uploaded with response: {response.status_code}, {response.text}")
