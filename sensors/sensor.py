import os
import time
import random
import requests
from datetime import datetime, timezone

sensor_id = int(os.environ["SENSOR_ID"])
lat = float(os.environ["LAT"])
lon = float(os.environ["LON"])
sensor_type = os.environ["SENSOR_TYPE"]
flask_url = os.environ.get("FLASK_URL", "http://flask-app:5000")
interval = int(os.environ.get("INTERVAL", "10"))


def generate_value(sensor_type):
    if sensor_type == "Temperature Sensor":
        return round(random.uniform(10, 30), 2)
    if sensor_type == "Pressure Sensor":
        return round(random.uniform(980, 1035), 2)
    if sensor_type == "Air Quality Sensor":
        return round(random.uniform(0, 150), 2)
    if sensor_type == "CO2 Sensor":
        return round(random.uniform(350, 1200), 2)
    return round(random.uniform(0, 100), 2)


while True:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    value = generate_value(sensor_type)

    try:
        r = requests.get(
            f"{flask_url}/store",
            params={
                "sensor_id": sensor_id,
                "lat": lat,
                "lon": lon,
                "type": sensor_type,
                "timestamp": timestamp,
                "value": value,
            },
            timeout=5,
        )
        print(f"Sent: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Send failed: {e}")

    time.sleep(interval)
