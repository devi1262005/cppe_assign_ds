import csv
import random
from datetime import datetime, timedelta

start = datetime(2025, 11, 3, 0, 0, 0)
rows = []

for day in range(7): 
    for hour in range(24):
        timestamp = start + timedelta(days=day, hours=hour)
        traffic = random.randint(10, 150)
        prediction = 1 if traffic > 100 else 0
        rows.append([timestamp.strftime("%Y-%m-%d %H:%M:%S"), traffic, prediction])

with open("traffic_predictions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "traffic_density", "prediction"])
    writer.writerows(rows)

print("Data saved to traffic_predictions.csv")
