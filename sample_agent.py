#!/usr/bin/env python

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_update', methods=['POST'])
def receive_update():
    """Receives updates from Managing Agent (Agent 3)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data format"}), 400

    print(f"📢 Agent 2 Received Update: {data}")

    return jsonify({"status": "Update received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # Runs on port 5002
