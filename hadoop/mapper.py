#!/usr/bin/env python3
import sys
import math

if len(sys.argv) != 4:
    print("Usage: mapper.py <D_km> <X_lat> <Y_lon>", file=sys.stderr)
    sys.exit(1)

D = float(sys.argv[1])   # distance in km
X = float(sys.argv[2])   # center latitude
Y = float(sys.argv[3])   # center longitude

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

first_line = True
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    # Skip header
    if first_line and line.startswith("sensor_id,"):
        first_line = False
        continue
    first_line = False

    parts = line.split(",")
    if len(parts) != 5:
        continue

    try:
        sensor_id = parts[0]
        lat = float(parts[1])
        lon = float(parts[2])
        timestamp = parts[3]
        value = float(parts[4])
    except ValueError:
        continue

    dist = haversine(X, Y, lat, lon)

    if dist <= D:
        print(f"stats\t{value}")
