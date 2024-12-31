import requests

INFLUXDB_URL = 'http://localhost:8086/query'

def create_database(db_name):
    query = f"CREATE DATABASE {db_name}"
    params = {
        'q': query
    }

    response = requests.post(INFLUXDB_URL, params=params)
    if response.status_code == 200:
        print(f"Database '{db_name}' created successfully.")
    else:
        print(f"Error creating database: {response.text}")

# Call the function to create the database
create_database('AquaDB')
