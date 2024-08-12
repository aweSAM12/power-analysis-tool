from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

powertop_csv_data = """
Usage;Wakeups/s;GPU ops/s;Disk IO/s;GFX Wakeups/s;Category;Description;PW Estimate
172.9;24.9;;;;Timer;tick_sched_timer;98.5 mW
296.0;22.9;;;;Process;[PID 313728] /usr/bin/containerd;90.8 mW
96.5;16.2;;;;Process;[PID 11] [rcu_sched];64.2 mW
225.5;14.1;;;;Process;[PID 313736] /usr/bin/containerd;56.0 mW
409.9;12.3;;;;Process;[PID 361909] /usr/bin/vmtoolsd;49.4 mW
232.0;12.1;;;;Process;[PID 313737] /usr/bin/containerd;48.3 mW
"""


def parse_powertop_data(csv_data):
    power_data = {}
    reader = csv.DictReader(csv_data.strip().split('\n'), delimiter=';')
    for row in reader:
        description = row['Description']
        if 'PID' in description:
            pid = int(description.split(' ')[1].strip('[]'))
            power_estimate = row['PW Estimate']
            # Strip the 'mW' unit and convert to float
            if 'mW' in power_estimate:
                power_estimate = float(power_estimate.replace(' mW', ''))
            power_data[pid] = power_estimate / 1000.0  # Convert to Watts
    return power_data


power_data = parse_powertop_data(powertop_csv_data)

@app.route('/power', methods=['GET'])
def get_power():
    pid = request.args.get('pid', type=int)
    
    if pid is None:
        return jsonify({'error': 'Missing required parameter: pid'}), 400
    
    power_consumption = power_data.get(pid, None)
    if power_consumption is None:
        return jsonify({'error': 'PID not found'}), 404

    return jsonify({'pid': pid, 'power_consumption_w': power_consumption})

if __name__ == '__main__':
    app.run(debug=True)
