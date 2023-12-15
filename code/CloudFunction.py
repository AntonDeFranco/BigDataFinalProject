import requests
import json
from google.cloud import pubsub_v1
import time
from datetime import datetime

# Configuration
OWM_API_KEY = 'e6522cea6f36f1540bcabaf84cb0b1c0'
CHICAGO_LAT, CHICAGO_LON = 41.8781, -87.6298  # Coordinates for Chicago
PUBSUB_PROJECT_ID = 'bionic-flux-406717'
PUBSUB_TOPIC = 'chicago-weather-anomalies'
SLEEP_INTERVAL = 3600  # 1 hour in seconds

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PUBSUB_PROJECT_ID, PUBSUB_TOPIC)

def fetch_weather_data():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={CHICAGO_LAT}&lon={CHICAGO_LON}&appid={OWM_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch weather data")

def transform_data_for_bigquery(weather_data):
    # Extracting main weather data
    weather_main = weather_data['main']
    wind_data = weather_data['wind']
    weather_desc = weather_data['weather'][0] if weather_data['weather'] else {}
    sys_data = weather_data.get('sys', {})

    transformed_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "latitude": CHICAGO_LAT,
        "longitude": CHICAGO_LON,
        "temperature": weather_main.get("temp"),
        "humidity": weather_main.get("humidity"),
        "pressure": weather_main.get("pressure"),
        "wind_speed": wind_data.get("speed"),
        "wind_deg": wind_data.get("deg"),
        "clouds": weather_data.get("clouds", {}).get("all", 0),
        "visibility": weather_data.get("visibility"),
        "weather_main": weather_desc.get("main"),
        "weather_description": weather_desc.get("description"),
        "temp_min": weather_main.get("temp_min"),
        "temp_max": weather_main.get("temp_max"),
        "feels_like": weather_main.get("feels_like"),
        "sea_level": weather_main.get("sea_level"),
        "grnd_level": weather_main.get("grnd_level"),
        "sunrise": sys_data.get("sunrise"),
        "sunset": sys_data.get("sunset"),
        # Add any additional fields as per your BigQuery schema
    }
    return transformed_data


def publish_to_pubsub(data):
    data_str = json.dumps(data)
    publisher.publish(topic_path, data_str.encode('utf-8'))

def main(request):
    try:
        weather_data = fetch_weather_data()
        transformed_data = transform_data_for_bigquery(weather_data)
        publish_to_pubsub(transformed_data)
        return 'Weather data published successfully', 200
    except Exception as e:
        return f'An error occurred: {str(e)}', 500
