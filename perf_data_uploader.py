import subprocess
import csv
import time
from datetime import datetime

def parse_perf_output(output):
    # Extract power consumption value in joules
    for line in output.splitlines():
        if "Joules power/energy-pkg/" in line:
            # Get the power consumption value (in joules) and convert it to watts
            energy_joules = float(line.split()[0])
            power_watts = energy_joules / 60  # Convert joules to watts (since sleep is 60 seconds)
            return power_watts
    return None

def write_to_csv(timestamp, power_consumption_w):
    with open("power_consumption.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, power_consumption_w])

def main():
    while True:
        # Run the perf command
        result = subprocess.run(["perf", "stat", "-a", "-e", "power/energy-pkg/", "sleep", "60"], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Parse the output to get power consumption
        power_consumption_w = parse_perf_output(result.stderr)  # perf outputs to stderr

        if power_consumption_w is not None:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Write data to CSV
            write_to_csv(timestamp, power_consumption_w)

        # Wait 60 seconds before the next measurement
        time.sleep(60)

if __name__ == "__main__":
    # Create CSV and write header if it doesn't exist
    with open("power_consumption.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "power_consumption_w"])

    # Start the monitoring loop
    main()
