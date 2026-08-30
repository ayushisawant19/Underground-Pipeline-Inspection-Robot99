import os
import csv
import base64
import datetime
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

STORAGE_DIR = "crack_detection_frames"
CSV_FILE = "rover_telemetry_database.csv"
os.makedirs(STORAGE_DIR, exist_ok=True)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Front_cm", "Rear_cm", "Left_cm", "Right_cm", "Pitch_deg", "Roll_deg", "Gas_Raw", "CH4_pct", "Battery_Volts", "Battery_Pct"])

telemetry_store = {
    "us_front_cm": 145.0, "us_rear_cm": 210.0, "us_left_cm": 35.5, "us_right_cm": 42.0,
    "pitch_deg": -0.67, "roll_deg": -0.13, "battery_pct": 88, "battery_volts": 18.2,
    "gas_raw": 340, "ch4_pct": 0.12, "distance_covered_m": 23.40
}

inspection_history = [
    {"id": "RUN-001", "date": "2026-08-28", "start_time": "10:15:00 AM", "end_time": "11:00:00 AM", "distance": "45.2 m", "max_gas": "420 (Safe)", "status": "COMPLETED"},
    {"id": "RUN-002", "date": datetime.datetime.now().strftime("%Y-%m-%d"), "start_time": "01:00:00 PM", "end_time": "IN PROGRESS", "distance": "23.4 m", "max_gas": "340 (Safe)", "status": "ACTIVE"}
]

@app.route('/api/rover-telemetry', methods=['POST'])
def receive_telemetry():
    data = request.json
    if data:
        for k in telemetry_store.keys():
            if k in data: telemetry_store[k] = data[k]
        telemetry_store["ch4_pct"] = round((telemetry_store["gas_raw"] / 4095.0) * 100, 2)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CSV_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, telemetry_store["us_front_cm"], telemetry_store["us_rear_cm"], telemetry_store["us_left_cm"], telemetry_store["us_right_cm"], telemetry_store["pitch_deg"], telemetry_store["roll_deg"], telemetry_store["gas_raw"], telemetry_store["ch4_pct"], telemetry_store["battery_volts"], telemetry_store["battery_pct"]])
    return jsonify({"status": "logged_to_csv"})

@app.route('/api/diagnostics', methods=['GET'])
def get_diagnostics(): return jsonify(telemetry_store)

@app.route('/api/rover-history', methods=['GET'])
def get_history(): return jsonify(inspection_history)

@app.route('/api/save-frame', methods=['POST'])
def save_frame():
    image_base64 = request.json.get('image_data')
    if image_base64:
        filename = os.path.join(STORAGE_DIR, f"frame_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        with open(filename, "wb") as f: f.write(base64.b64decode(image_base64.split(",")[1]))
        return jsonify({"status": "success", "file": filename})
    return jsonify({"status": "failed"}), 400

@app.route('/api/auto-detect-crack', methods=['POST'])
def api_auto_detect():
    data = request.json
    image_base64 = data.get('image_data')
    if image_base64:
        header, encoded = image_base64.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            crack_found = False
            max_len = 0.0
            for c in contours:
                length = cv2.arcLength(c, True)
                if length > 40:
                    crack_found = True
                    if length > max_len: max_len = length
            return jsonify({"crack_detected": crack_found, "severity_score": round(float(max_len), 2)})
    return jsonify({"crack_detected": False, "severity_score": 0.0})

@app.route('/api/control', methods=['POST'])
def handle_control():
    print(f"[MOTOR COMMAND]: {request.json.get('action', 'STOP')}")
    return jsonify({"status": "executed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    