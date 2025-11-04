import random, time, json, boto3

s3 = boto3.client('s3')
BUCKET_NAME = 'traffic-sensor-data-bucket'

while True:
    data = {
        "sensor_id": f"sensor-{random.randint(1,5)}",
        "location": random.choice(["Chennai","Bangalore","Delhi"]),
        "traffic_density": random.randint(10,100),
        "air_quality_index": random.randint(50,300),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    file_name = f"data_{int(time.time())}.json"
    s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=json.dumps(data))
    print(f"Uploaded {file_name}")
    time.sleep(5)
