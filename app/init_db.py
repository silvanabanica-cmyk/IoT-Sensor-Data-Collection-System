import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "data", "sensors.db"))
SCHEMA_PATH = os.environ.get("SCHEMA_PATH", os.path.join(BASE_DIR, "schema.sql"))

DEFAULT_TYPES = [
    ("Temperature Sensor", "°C"),
    ("Pressure Sensor", "hPa"),
    ("Air Quality Sensor", "PM10"),
    ("CO2 Sensor", "ppm"),
]

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    for sensor_type, unit in DEFAULT_TYPES:
        conn.execute(
            """
            INSERT OR IGNORE INTO sensor_types(sensor_type, unit)
            VALUES (?, ?)
            """,
            (sensor_type, unit),
        )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    main()
