import pandas as pd
import os
from datetime import datetime, timedelta

class CSVHandler:
    def __init__(self, upload_folder='uploads'):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)
        self.main_csv = os.path.join(self.upload_folder, 'combined_power_consumption.csv')
        if not os.path.exists(self.main_csv):
            pd.DataFrame(columns=['client_name', 'data', 'timestamp', 'power_consumption_w', 'app_name']).to_csv(self.main_csv, index=False)

    def save_data(self, client_name, data):
        data['client_name'] = client_name
        if os.path.exists(self.main_csv):
            existing_data = pd.read_csv(self.main_csv)
            combined_data = pd.concat([existing_data, data], ignore_index=True)
        else:
            combined_data = data
        combined_data.to_csv(self.main_csv, index=False)

    def upload_csv(self, file, client_name):
        if file.filename == '':
            return {'error': 'No selected file'}, 400
        if file and file.filename.endswith('.csv'):
            data = pd.read_csv(file)
            client_name = client_name.split('_')[0]  # Extract actual client name
            self.save_data(client_name, data)
            return {'message': 'File uploaded and data saved successfully'}, 200
        else:
            return {'error': 'Invalid file type'}, 400

    def get_data(self):
        if os.path.exists(self.main_csv):
            return pd.read_csv(self.main_csv).to_dict(orient='records')
        else:
            return []

    def query_power_data(self,start_time, app_name, client_name):
        power_data = []
        with open(self.main_csv, 'r') as f:
            reader = pd.read_csv(f)
            for _, row in reader.iterrows():
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                if timestamp >= start_time and row['app_name'] == app_name and row['client_name'] == client_name:
                    power_data.append({
                        'timestamp': timestamp,
                        'power_consumption_w': float(row['power_consumption_w']),
                        'app_name': row['app_name'],
                        'client_name': row['client_name']
                    })
        
        grouped_data = {}
        for entry in power_data:
            hour_diff = int((datetime.now() - entry['timestamp']).total_seconds() // 3600)
            if hour_diff not in grouped_data:
                grouped_data[hour_diff] = []
            grouped_data[hour_diff].append({
                'timestamp': entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'power_consumption_w': entry['power_consumption_w'],
                'app_name': entry['app_name'],
                'client_name': entry['client_name']
            })
        
        # Ensure all hours within the range are included, even if empty
        max_hour_diff = int((datetime.now() - start_time).total_seconds() // 3600)
        for hour in range(max_hour_diff + 1):
            if hour not in grouped_data:
                grouped_data[hour] = []
        
        return grouped_data

    def parse_frequency(self,frequency):
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
