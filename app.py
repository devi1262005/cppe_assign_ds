from flask import Flask, request, jsonify
import joblib
import csv
from datetime import datetime, timedelta
import pandas as pd
import random
app = Flask(__name__)

try:
    model = joblib.load('traffic_model.pkl')
except Exception as e:
    model = None
    print("Could not load model:", e)

API_TOKEN = "mysecret123"

@app.before_request
def log_request_info():
    with open("access_audit.log", "a") as f:
        f.write(f"{datetime.now()} | {request.remote_addr} | {request.path}\n")

@app.route('/')
def home():
    return jsonify({"message": "Traffic AI API is running! Use POST /predict with Authorization header."})

@app.route('/predict', methods=['POST'])
def predict():

    token = request.headers.get('Authorization')
    if token != f"Bearer {API_TOKEN}":
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True)
    if not data or 'traffic_density' not in data:
        return jsonify({'error': 'Missing traffic_density in JSON body'}), 400

    try:
        traffic = float(data['traffic_density'])
        pred = model.predict([[traffic]])[0]

        if int(pred) == 1:
            suggestion = "Increase signal wait time — possible congestion detected."
        else:
            suggestion = "Normal signal timing — air quality is acceptable."

        with open("predictions_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), traffic, int(pred)])

        return jsonify({
            'prediction': int(pred),
            'suggestion': suggestion
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_week_data():
    start = datetime(2025, 11, 3, 0, 0, 0)
    rows = []
    for day in range(7):
        for hour in range(24):
            timestamp = start + timedelta(days=day, hours=hour)
            traffic = random.randint(10, 150)
            prediction = 1 if traffic > 100 else 0
            rows.append([timestamp, traffic, prediction])
    df = pd.DataFrame(rows, columns=["timestamp", "traffic_density", "prediction"])
    df["day"] = df["timestamp"].dt.day_name()
    return df

df = generate_week_data()

def daily_summary():
    summary = df.groupby("day").agg({
        "traffic_density": "mean",
        "prediction": "sum"
    }).rename(columns={
        "traffic_density": "avg_traffic_density",
        "prediction": "poor_air_events"
    }).reset_index()

    # Ensure day order
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    summary["day"] = pd.Categorical(summary["day"], categories=day_order, ordered=True)
    summary = summary.sort_values("day")
    return summary

def adaptive_suggestions(summary):
    tips = []
    for _, row in summary.iterrows():
        day = row["day"]
        traffic = row["avg_traffic_density"]
        poor_air = row["poor_air_events"]

        if poor_air > 10:
            tips.append(f"{day}: Heavy pollution — activate green-light optimization and restrict heavy vehicles.")
        elif traffic > 100:
            tips.append(f"{day}: High traffic — extend green light duration on main routes.")
        elif traffic < 70:
            tips.append(f"{day}: Low traffic — normal operation sufficient.")
    return tips



@app.route('/dashboard')
def dashboard():
    try:
        df = pd.read_csv('traffic_predictions.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day'] = df['timestamp'].dt.day_name()

        summary = df.groupby('day').agg({'traffic_density':'mean', 'prediction':'mean'}).reset_index()
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        summary['day'] = pd.Categorical(summary['day'], categories=day_order, ordered=True)
        summary = summary.sort_values('day')

        messages = []
        for _, row in summary.iterrows():
            if row['traffic_density'] > 100:
                msg = f"{row['day']}: Heavy traffic — increase green light duration, monitor pollution sensors closely."
            elif row['traffic_density'] > 60:
                msg = f"{row['day']}: Moderate traffic — monitor air quality closely."
            else:
                msg = f"{row['day']}: Light traffic — air quality is stable."
            messages.append(msg)

        labels = summary['day'].tolist()
        traffic_values = summary['traffic_density'].round(1).tolist()
        pred_values = summary['prediction'].round(2).tolist()

        return f"""
        <html>
        <head>
          <title>Traffic Dashboard</title>
          <meta http-equiv="refresh" content="60">
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body style='font-family:sans-serif;background:#f9fafc;padding:20px;'>
          <h2>Real-Time Traffic and Air Quality</h2>
          <canvas id="chart" width="400" height="200"></canvas>
          <script>
            const ctx = document.getElementById('chart');
            const chart = new Chart(ctx, {{
              type: 'bar',
              data: {{
                labels: {labels},
                datasets: [
                  {{
                    label: 'Avg Traffic Density',
                    data: {traffic_values},
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderWidth: 1
                  }},
                  {{
                    label: 'Avg Air Quality (Pred)',
                    data: {pred_values},
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderWidth: 1
                  }}
                ]
              }},
              options: {{ scales: {{ y: {{ beginAtZero: true }} }} }}
            }});
          </script>
          <h3>Adaptive Control Strategies</h3>
          {"<br>".join(messages)}
        </body>
        </html>
        """
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report')
def report():
    try:
        df = pd.read_csv("predictions_log.csv", header=None, names=["Time", "Traffic", "Prediction"])
        summary = df.groupby("Prediction").size().to_dict()
        return jsonify({
            "total_predictions": len(df),
            "summary": summary
        })
    except Exception:
        return jsonify({"message": "No prediction data available yet."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
