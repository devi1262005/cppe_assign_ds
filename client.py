import requests
import json

url = "http://127.0.0.1:8080/predict"  
headers = {
    "Authorization": "Bearer mysecret123",
    "Content-Type": "application/json"
}
data = {"traffic_density": 120}

response = requests.post(url, headers=headers, data=json.dumps(data))

print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response Text:", response.text)
