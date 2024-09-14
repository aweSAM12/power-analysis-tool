import subprocess
import csv
import time
from datetime import datetime
import threading
import os
import argparse

def parse_perf_output(line, frequency):
    if "Joules power/energy-pkg/" in line:
        energy_joules = round(float(line.split()[1].replace(",", "")),2)
        power_watts = round(energy_joules / (frequency / 1000),2)
        return power_watts
    return None

def write_to_csv(timestamp, power_consumption_w, app_name):
    with open("power_consumption.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, power_consumption_w, app_name])

def read_output(pipe, callback, app_name, frequency):
    for line in iter(pipe.readline, ''):
        line = line.strip()
        # print(f"Debug: Raw line: {line}")  # Debug statement
        power_consumption_w = parse_perf_output(line, frequency)
        if power_consumption_w is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Debug: Parsed power (W): {power_consumption_w}")  # Debug statement
            callback(timestamp, power_consumption_w, app_name)
    pipe.close()

def extract_app_name(command):
    return os.path.basename(command.split()[1])

def main(command, frequency, timeout):
    app_name = extract_app_name(command)
    perf_command = ["sudo", "perf", "stat", "-e", "power/energy-pkg/", "-I", str(frequency)] + command.split()
    print(perf_command)
    process = subprocess.Popen(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout_thread = threading.Thread(target=read_output, args=(process.stdout, write_to_csv, app_name, frequency))
    stderr_thread = threading.Thread(target=read_output, args=(process.stderr, write_to_csv, app_name, frequency))

    stdout_thread.start()
    stderr_thread.start()

    def stop_process():
        process.terminate()
        stdout_thread.join()
        stderr_thread.join()

    timer = threading.Timer(timeout, stop_process)
    timer.start()

    process.wait()
    stdout_thread.join()
    stderr_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor power consumption of an application.")
    parser.add_argument("command", type=str, help="Command to execute the application (e.g., 'sh app.sh' or 'python app.py').")
    parser.add_argument("frequency", type=int, help="Frequency in milliseconds to take inputs (e.g., 1000 for 1 second).")
    parser.add_argument("timeout", type=int, help="Timeout in seconds to stop the execution.")
    args = parser.parse_args()

    if not os.path.exists("power_consumption.csv") or os.path.getsize("power_consumption.csv") == 0:
        with open("power_consumption.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "power_consumption_w", "app_name"])

    main(args.command, args.frequency, args.timeout)
