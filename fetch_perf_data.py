from flask import Flask, request, jsonify, render_template
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import csv
import subprocess
from datetime import datetime, timedelta
import os
import logging
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

PERF_LOG_FILE = 'power_consumption.csv'  # Update with the file created by the perf script

def query_power_data(start_time, app_name):
    power_data = []
    with open(PERF_LOG_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            if timestamp >= start_time and row['app_name'] == app_name:
                power_data.append({
                    'timestamp': timestamp,
                    'power_consumption_w': float(row['power_consumption_w']),
                    'app_name': row['app_name']
                })
    
    grouped_data = {}
    for entry in power_data:
        hour_diff = int((datetime.now() - entry['timestamp']).total_seconds() // 3600)
        if hour_diff not in grouped_data:
            grouped_data[hour_diff] = []
        grouped_data[hour_diff].append({
            'timestamp': entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'power_consumption_w': entry['power_consumption_w'],
            'app_name': entry['app_name']
        })
    
    # Ensure all hours within the range are included, even if empty
    max_hour_diff = int((datetime.now() - start_time).total_seconds() // 3600)
    for hour in range(max_hour_diff + 1):
        if hour not in grouped_data:
            grouped_data[hour] = []
    
    return grouped_data

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
        raise ValueError("Invalid frequency format. Use '10m', '1h', or '1d'.")

@app.route('/power', methods=['GET'])
def get_power():
    frequency = request.args.get('frequency', default='1h', type=str)
    app_name = request.args.get('app_name', type=str)
    
    if not app_name:
        return jsonify({'error': 'app_name parameter is required'}), 400
    
    try:
        start_time = parse_frequency(frequency)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    power_data = query_power_data(start_time, app_name)
    
    if not power_data:
        return jsonify({'error': 'No data available for the specified time range and app_name'}), 404

    formatted_data = {}
    for hour in sorted(power_data.keys()):
        formatted_data[f'last {hour + 1} hrs'] = power_data[hour]
    
    return jsonify({'data': formatted_data, 'frequency': frequency, 'app_name': app_name})



@app.route('/plot', methods=['GET', 'POST'])
def plot_power():
    if request.method == 'GET':
        return render_template('plot_form.html')
    
    elif request.method == 'POST':
        app_name = request.form.get('app_name')
        frequency = request.form.get('frequency')

        if not app_name:
            return jsonify({'error': 'app_name parameter is required'}), 400

        try:
            start_time = parse_frequency(frequency)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        power_data = query_power_data(start_time, app_name)

        if not power_data:
            return jsonify({'error': 'No data available for the specified time range and app_name'}), 404

        # Flatten the data for plotting
        timestamps = []
        power_values = []
        for hour_data in power_data.values():
            for entry in hour_data:
                timestamps.append(entry['timestamp'])
                power_values.append(entry['power_consumption_w'])

        # Calculate the average value
        average_value = np.mean(power_values)

        # Create a Plotly figure
        fig = make_subplots()

        # Add traces: green for below average, red for above average
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=[value if value <= average_value else None for value in power_values],
            mode='lines+markers',
            line=dict(color='green'),
            name='Below Average'
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=[value if value > average_value else None for value in power_values],
            mode='lines+markers',
            line=dict(color='red'),
            name='Above Average'
        ))

        # Add a horizontal line for the average
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=[average_value] * len(timestamps),
            mode='lines',
            line=dict(color='blue', dash='dash'),
            name=f'Average ({average_value:.2f} W)'
        ))

        # Update layout
        fig.update_layout(
            title=f'Power Consumption for {app_name}',
            xaxis_title='Timestamp',
            yaxis_title='Power Consumption (W)',
            xaxis=dict(tickformat='%Y-%m-%d %H:%M', tickangle=-45),
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=40, b=40)
         
        )

        # Convert the plot to a div string for embedding in HTML
        plot_div = fig.to_html(full_html=False)

        return render_template('plot.html', plot_div=plot_div, app_name=app_name, frequency=frequency)

@app.route('/update_plot', methods=['POST'])
def update_plot():
    app_name = request.form.get('app_name')
    frequency = request.form.get('frequency')

    if not app_name:
        return jsonify({'error': 'app_name parameter is required'}), 400

    try:
        start_time = parse_frequency(frequency)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    power_data = query_power_data(start_time, app_name)

    if not power_data:
        return jsonify({'error': 'No data available for the specified time range and app_name'}), 404

    # Flatten the data for plotting
    timestamps = []
    power_values = []
    for hour_data in power_data.values():
        for entry in hour_data:
            timestamps.append(entry['timestamp'])
            power_values.append(entry['power_consumption_w'])

    # Calculate the average value
    average_value = np.mean(power_values)

    # Create a Plotly figure
    fig = make_subplots()

    # Add traces: green for below average, red for above average
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=[value if value <= average_value else None for value in power_values],
        mode='lines+markers',
        line=dict(color='green'),
        name='Below Average'
    ))

    fig.add_trace(go.Scatter(
        x=timestamps,
        y=[value if value > average_value else None for value in power_values],
        mode='lines+markers',
        line=dict(color='red'),
        name='Above Average'
    ))

    # Add a horizontal line for the average
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=[average_value] * len(timestamps),
        mode='lines',
        line=dict(color='blue', dash='dash'),
        name=f'Average ({average_value:.2f} W)'
    ))

    # Update layout
    fig.update_layout(
        title=f'Power Consumption for {app_name}',
        xaxis_title='Timestamp',
        yaxis_title='Power Consumption (W)',
        xaxis=dict(tickformat='%Y-%m-%d %H:%M', tickangle=-45),
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40)
       
    )

    # Convert the plot to a div string for embedding in HTML
    plot_div = fig.to_html(full_html=False)

    return render_template('plot.html', plot_div=plot_div, app_name=app_name, frequency=frequency)

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.json
    command = data.get('command')
    frequency = data.get('frequency', '1000')
    timeout = data.get('timeout', 60)  # Default timeout is 60 seconds
    
    if not command:
        return jsonify({'error': 'command parameter is required'}), 400
    
    try:
        command = f'sudo python3 /home/user/samarth/power-analysis-tool/perf_data_uploader.py "{command}" {frequency} {timeout}'
        print(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return jsonify({
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode,
            'frequency': frequency,
            'timeout': timeout,
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timed out'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True)
