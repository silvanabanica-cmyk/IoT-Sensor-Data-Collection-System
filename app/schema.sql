PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id INTEGER PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_type TEXT NOT NULL UNIQUE CHECK(sensor_type <> ''),
    unit TEXT NOT NULL CHECK(unit <> '')
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    timestamp_utc TEXT NOT NULL CHECK(timestamp_utc <> ''),
    value REAL NOT NULL,
    FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES sensor_types(type_id) ON DELETE CASCADE
);
