#!/usr/bin/env python3
import sys

count = 0
total = 0.0
min_val = None
max_val = None

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split("\t")
    if len(parts) != 2:
        continue

    try:
        value = float(parts[1])
    except ValueError:
        continue

    count += 1
    total += value

    if min_val is None or value < min_val:
        min_val = value
    if max_val is None or value > max_val:
        max_val = value

if count == 0:
    print("No values found within the specified distance.")
else:
    avg_val = total / count
    print(f"count\t{count}")
    print(f"min\t{min_val}")
    print(f"max\t{max_val}")
    print(f"avg\t{avg_val}")
