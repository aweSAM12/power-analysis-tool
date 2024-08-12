import subprocess
import time
import csv
from datetime import datetime, timedelta

LOG_FILE = 'powertop_output.csv'
LOG_DURATION_HOURS = 24

def run_powertop():
    result = subprocess.run(['powertop', '--csv'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def parse_powertop_data(csv_data):
    parsed_data = []
    reader = csv.DictReader(csv_data.strip().split('\n'), delimiter=';')
    for row in reader:
        description = row['Description']
        if 'PID' in description:
            pid = int(description.split(' ')[1].strip('[]'))
            power_estimate = row['PW Estimate']
            if 'mW' in power_estimate:
                power_estimate = float(power_estimate.replace(' mW', '')) / 1000.0  
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            parsed_data.append({'timestamp': timestamp, 'pid': pid, 'power_consumption_w': power_estimate})
    return parsed_data

def log_powertop_data():
    csv_data = run_powertop()
    parsed_data = parse_powertop_data(csv_data)

    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'pid', 'power_consumption_w'])
        if f.tell() == 0:
            writer.writeheader()  
        writer.writerows(parsed_data)

def purge_old_logs():
    cutoff_time = datetime.now() - timedelta(hours=LOG_DURATION_HOURS)
    with open(LOG_FILE, 'r') as f:
        rows = list(csv.DictReader(f))

    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'pid', 'power_consumption_w'])
        writer.writeheader()
        for row in rows:
            if datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S') > cutoff_time:
                writer.writerow(row)

if __name__ == '__main__':
    log_powertop_data()
    purge_old_logs()
