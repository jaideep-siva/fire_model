#!/usr/bin/env python

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

LISTENING_AGENT_URL = "http://localhost:5002/receive_update"  # URL of Agent 2

@app.route('/receive_alert', methods=['POST'])
def receive_alert():
    """Receives fire alert from Agent 1 and forwards it to Agent 2."""
    try:
        data = request.get_json()
        if not data or "latitude" not in data or "longitude" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        print(f"🚨 Managing Agent Received Alert: {data}")

        # Forward alert to Listening Agent (Agent 2)
        response = requests.post(LISTENING_AGENT_URL, json=data)
        print(f"📢 Alert forwarded to Agent 2 | Response: {response.status_code}")

        return jsonify({"status": "Alert processed"}), 200
    except Exception as e:
        print(f"⚠️ Error in Managing Agent: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)  # Runs on port 5003
