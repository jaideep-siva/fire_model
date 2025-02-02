#!/usr/bin/env python

import cv2
import os
import sys
import getopt
import signal
import time
import requests
from edge_impulse_linux.image import ImageImpulseRunner

# Global Variables
runner = None
show_camera = True
fire_threshold = 0.93
consecutive_fire_count = 0
fire_detection_required_count = 10  # Number of consecutive detections required

# Fake GPS coordinates (can be replaced with real sensor input)
FAKE_LATITUDE = 37.7749  # Example: San Francisco
FAKE_LONGITUDE = -122.4194
MANAGING_AGENT_URL = "http://localhost:5003/receive_alert"  # URL of Agent 3

if sys.platform == 'linux' and not os.environ.get('DISPLAY'):
    show_camera = False

def now():
    return round(time.time() * 1000)

def send_alert():
    """Send fire alert with coordinates to Managing Agent (Agent 3)."""
    global FAKE_LATITUDE, FAKE_LONGITUDE, MANAGING_AGENT_URL
    data = {"latitude": FAKE_LATITUDE, "longitude": FAKE_LONGITUDE, "alert": "Fire detected"}
    try:
        response = requests.post(MANAGING_AGENT_URL, json=data)
        print(f"🔥 Alert sent to Managing Agent: {data} | Response: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to send alert: {e}")

def fetch_and_process_results(res):
    """Process classification results and check fire confidence."""
    global consecutive_fire_count, fire_threshold, fire_detection_required_count

    if "classification" in res["result"].keys():
        print(f'Result ({res["timing"]["dsp"] + res["timing"]["classification"]} ms.) ', end='')
        fire_detected = False
        for label, score in res['result']['classification'].items():
            print(f'{label}: {score:.2f}\t', end='')
            if label.lower() == "fire" and score > fire_threshold:
                fire_detected = True
        print('', flush=True)

        if fire_detected:
            consecutive_fire_count += 1
        else:
            consecutive_fire_count = 0

        # If fire is detected for required consecutive iterations, send alert
        if consecutive_fire_count >= fire_detection_required_count:
            print("🔥 Fire detected consistently! Sending alert...")
            send_alert()
            consecutive_fire_count = 0  # Reset after sending

def main(argv):
    if len(argv) < 1:
        sys.exit(2)

    model = argv[0]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print(f'MODEL: {modelfile}')

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print(f'Loaded runner for "{model_info["project"]["owner"]} / {model_info["project"]["name"]}"')

            for res, img in runner.classifier(0):  # Assuming camera at index 0
                fetch_and_process_results(res)

                if show_camera:
                    cv2.imshow('Monitoring Agent', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) == ord('q'):
                        break
        finally:
            if runner:
                runner.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
