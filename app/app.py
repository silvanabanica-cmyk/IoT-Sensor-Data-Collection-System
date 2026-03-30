import os
import sqlite3
from collections import defaultdict
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "data", "sensors.db"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def bad_request(message):
    return jsonify({"status": "error", "message": message}), 400


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "IoT Sensor API is running"})


@app.route("/types")
def types():
    conn = get_db()
    rows = conn.execute(
        "SELECT type_id, sensor_type, unit FROM sensor_types ORDER BY sensor_type"
    ).fetchall()
    conn.close()

    return jsonify(
        [
            {
                "type_id": row["type_id"],
                "sensor_type": row["sensor_type"],
                "unit": row["unit"],
            }
            for row in rows
        ]
    )


@app.route("/store")
def store():
    sensor_id = request.args.get("sensor_id")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    sensor_type = request.args.get("type")
    timestamp = request.args.get("timestamp")
    value = request.args.get("value")

    if not all([sensor_id, lat, lon, sensor_type, timestamp, value]):
        return bad_request("Missing one or more required parameters")

    try:
        sensor_id = int(sensor_id)
        lat = float(lat)
        lon = float(lon)
        value = float(value)
    except ValueError:
        return bad_request("sensor_id must be integer; lat/lon/value must be numeric")

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO sensors(sensor_id, latitude, longitude)
            VALUES (?, ?, ?)
            ON CONFLICT(sensor_id) DO UPDATE SET
                latitude=excluded.latitude,
                longitude=excluded.longitude
            """,
            (sensor_id, lat, lon),
        )

        type_row = conn.execute(
            "SELECT type_id FROM sensor_types WHERE sensor_type = ?",
            (sensor_type,),
        ).fetchone()

        if not type_row:
            conn.rollback()
            conn.close()
            return jsonify(
                {"status": "error", "message": f"Unknown sensor type: {sensor_type}"}
            ), 404

        conn.execute(
            """
            INSERT INTO measurements(sensor_id, type_id, timestamp_utc, value)
            VALUES (?, ?, ?, ?)
            """,
            (sensor_id, type_row["type_id"], timestamp, value),
        )

        conn.commit()
        return jsonify({"status": "success", "message": "Measurement stored"})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()


@app.route("/retrieve")
def retrieve():
    sensor_id = request.args.get("sensor_id")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if not all([sensor_id, start_time, end_time]):
        return bad_request("Missing sensor_id, start_time, or end_time")

    try:
        sensor_id = int(sensor_id)
    except ValueError:
        return bad_request("sensor_id must be an integer")

    conn = get_db()
    rows = conn.execute(
        """
        SELECT st.sensor_type, st.unit, m.timestamp_utc, m.value
        FROM measurements m
        JOIN sensor_types st ON m.type_id = st.type_id
        WHERE m.sensor_id = ?
          AND m.timestamp_utc >= ?
          AND m.timestamp_utc <= ?
        ORDER BY st.sensor_type, m.timestamp_utc
        """,
        (sensor_id, start_time, end_time),
    ).fetchall()
    conn.close()

    grouped = defaultdict(lambda: {"unit": "", "rows": []})

    for row in rows:
        grouped[row["sensor_type"]]["unit"] = row["unit"]
        grouped[row["sensor_type"]]["rows"].append(row)

    return render_template("retrieve.html", sensor_id=sensor_id, grouped=grouped)


@app.route("/fetch")
def fetch():
    sensor_type = request.args.get("type")
    if not sensor_type:
        return bad_request("Missing type parameter")

    conn = get_db()
    rows = conn.execute(
        """
        SELECT s.sensor_id, s.latitude, s.longitude, m.timestamp_utc, m.value
        FROM measurements m
        JOIN sensors s ON m.sensor_id = s.sensor_id
        JOIN sensor_types st ON m.type_id = st.type_id
        WHERE st.sensor_type = ?
        ORDER BY m.timestamp_utc
        """,
        (sensor_type,),
    ).fetchall()
    conn.close()

    header = "sensor_id,latitude,longitude,timestamp_utc,value\n"
    lines = [header]
    for row in rows:
        lines.append(
            f"{row['sensor_id']},{row['latitude']},{row['longitude']},{row['timestamp_utc']},{row['value']}\n"
        )

    content = "".join(lines)

    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={sensor_type}.txt"},
    )


@app.route("/add_type")
def add_type():
    sensor_type = request.args.get("type")
    unit = request.args.get("unit")

    if not sensor_type or not unit:
        return bad_request("Missing type or unit")

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO sensor_types(sensor_type, unit)
            VALUES (?, ?)
            """,
            (sensor_type, unit),
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Sensor type added"})
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
    finally:
        conn.close()


@app.route("/delete_type")
def delete_type():
    sensor_type = request.args.get("type")
    if not sensor_type:
        return bad_request("Missing type")

    conn = get_db()
    cur = conn.execute(
        "DELETE FROM sensor_types WHERE sensor_type = ?",
        (sensor_type,),
    )
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"status": "error", "message": "Sensor type not found"}), 404

    return jsonify(
        {
            "status": "success",
            "message": "Sensor type deleted; related measurements removed automatically",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
