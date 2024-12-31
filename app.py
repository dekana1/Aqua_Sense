from flask import Flask, render_template, request, jsonify
from influxdb_flask import InfluxDB
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import json
import pandas as pd
import pytz
import requests
import random
import subprocess
import time 
import threading

app = Flask(__name__)
# influxdb = InfluxDB(app)

## Set up InfluxDB connection parameters
influxdb_host = 'localhost'  # or the address where your InfluxDB is running
influxdb_port = 8086
influxdb_db = 'AquaDB'

# Initialize InfluxDB client
client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
client.switch_database(influxdb_db)

def run_external_script():
    subprocess.run(['python3', 'new_version_recevier.py'])


@app.route("/")
def index():

    return render_template('index.html'), 200


@app.route('/api/data/insert', methods=['POST'])
def insert_sensor_data():
    try:
        # Get JSON data from the request body
        data = request.get_json()
        
        #display_time = data['DisplayTime']  # assuming you send this as ISO formatted string or timestamp

        if data:
            print("Data to insert", data)
            # Extract sensor data (Make sure to adjust the field names as per your data)
            pipe_number = data['Pipe_n']
            time = data['Time']
            conductivity = data['Conductivity']
            level = data['Level']
            turbidity = data['Turbidity']
            # Prepare the data to be inserted
            json_body = [
                {
                    "measurement": "sensor_data",  # Measurement name (table in InfluxDB)
                    "tags": {
                        "pipe_number": pipe_number  # Optional: Can be used for identifying the sensor
                    },
                    "time": time,  # Timestamp (ISO format or UNIX timestamp)
                    "fields": {
                        "conductivity": conductivity,
                        "level": level,
                        "turbidity": turbidity
                    }
                }
            ]

            # Insert data into InfluxDB
            client.write_points(json_body)

        return jsonify({"message": "Data inserted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/get", methods=['GET'])
def get_data():
    # Define your local timezone as Beijing (CST, UTC+8)
    local_tz = pytz.timezone('Asia/Shanghai')

    # Get current local time in Beijing (CST)
    local_now = datetime.now(local_tz)

    # Convert local time (Beijing) to UTC for InfluxDB query
    utc_now = local_now.astimezone(pytz.utc)

    # Get time for one hour ago in UTC (to match InfluxDB time range)
    one_hour_ago_utc = utc_now - timedelta(hours=1)

    # Format the times for the query
    now_utc_str = utc_now.strftime('%Y-%m-%dT%H:%M:%SZ')
    one_hour_ago_utc_str = one_hour_ago_utc.strftime('%Y-%m-%dT%H:%M:%SZ')


    query = f'''
    SELECT "conductivity", "level", "turbidity" 
    FROM "sensor_data" 
    WHERE time >= '{one_hour_ago_utc_str}' AND time <= '{now_utc_str}'
    '''
    result = client.query(query)
    
    # Process the results into a format that can be used by Plotly
    points = []
    for point in result.get_points():
        time_utc = datetime.strptime(point['time'], '%Y-%m-%dT%H:%M:%SZ')
    
        # Convert UTC time to local Beijing time
        time_local = time_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
        
        # Format the local time (optional: you can format it differently)
        local_time_str = time_local.strftime('%Y-%m-%d %H:%M:%S')
        points.append({
            'time': local_time_str,
            'conductivity': point['conductivity'],
            'level': point['level'],
            'turbidity': point['turbidity']
        })
    
    # print(points)
    
    return jsonify(points)

    # return jsonify(generate_data())



# Sample data generation
# def generate_data():
#     data = {
#         "Pipe_n": None,
#         "Time": None,
#         "DisplayTime": None,
#         "Conductivity": None,
#         "Level": None,
#         "Turbidity": None
#     }


#     while True:

#         current_time = datetime.datetime.now()
#         data["Pipe_n"]= random.randint(1, 6)
#         data["Time"]= current_time.strftime("%Y-%m-%d %H:%M:%S")
#         data["DisplayTime"]=current_time.strftime("%H:%M")
#         # Generate random values for each sensor
#         data["Conductivity"]=round(random.uniform(0.1, 10.0), 2)  # conductivity in µS/cm
#         data["Level"]=round(random.uniform(0, 100), 2)  # level in percentage
#         data["Turbidity"]=round(random.uniform(0, 400), 2)

#         server_url = f"http://localhost:5000/api/data/insert"
#         response = requests.post(server_url, json=data)
#         if response.status_code == 200:
#             print("Data posted successfully: ", response.json())
#         else:
#             print("Failed to post: ", reponse.status_code, response.text)
        
#         time.sleep(60)
    
        # return data


threading.Thread(target=run_external_script, daemon=True).start()

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=True)

