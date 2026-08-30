import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so the frontend dashboard can communicate across origins
CORS(app)

# In-memory store for robot sensor readings and control states
robot_data = {
    "status": "online",
    "battery": 100,
    "gas_level": 0.0,
    "imu": {"pitch": 0.0, "roll": 0.0, "yaw": 0.0},
    "ultrasonic_distance": 0.0,
    "motor_command": "STOP"
}

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "Underground Pipeline Inspection Robot API",
        "status": "active",
        "data": robot_data
    }), 200

# Endpoint to fetch telemetry for the web dashboard
@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify(robot_data), 200

# Endpoint for ESP32/Arduino firmware modules to push sensor data
@app.route('/api/update', methods=['POST'])
def update_telemetry():
    global robot_data
    data = request.get_json(silent=True)
    if data:
        robot_data.update(data)
        return jsonify({"status": "success", "updated": data}), 200
    return jsonify({"status": "error", "message": "Invalid JSON format"}), 400

# Endpoint for UI buttons to issue motor movement commands
@app.route('/api/control', methods=['POST'])
def handle_control():
    global robot_data
    data = request.get_json(silent=True)
    if data and "command" in data:
        robot_data["motor_command"] = data["command"]
        return jsonify({"status": "success", "command": data["command"]}), 200
    return jsonify({"status": "error", "message": "Missing command key"}), 400

if __name__ == '__main__':
    # Use the dynamic port assigned by Render, falling back to 5000 locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    