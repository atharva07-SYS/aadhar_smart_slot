import requests
import json
import time
import subprocess
import sys
import threading

# Function to run the server in a separate thread
def run_server():
    subprocess.run([sys.executable, "server.py"], check=False)

def test_endpoints():
    base_url = "http://127.0.0.1:5000/api"
    
    # Allow server to start
    print("Waiting for server to start...")
    time.sleep(5) 

    # 1. Get Centers
    try:
        print("\nTesting GET /centers...")
        resp = requests.get(f"{base_url}/centers")
        print(f"Status: {resp.status_code}")
        print(f"Centers found: {len(resp.json())}")
        assert resp.status_code == 200
    except Exception as e:
        print(f"FAILED: {e}")

    # 2. Book Appointment
    try:
        print("\nTesting POST /book_appointment...")
        payload = {
            "request_type": "New Enrollment",
            "user_type": "Scheduled",
            "city": "New Delhi",
            "pincode": "110001"
        }
        resp = requests.post(f"{base_url}/book_appointment", json=payload)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Response: {data}")
        assert resp.status_code == 200
        assert data['success'] == True
    except Exception as e:
        print(f"FAILED: {e}")

    # 3. Get Stats
    try:
        print("\nTesting GET /stats...")
        resp = requests.get(f"{base_url}/stats")
        print(f"Status: {resp.status_code}")
        print(f"Stats: {resp.json()}")
        assert resp.status_code == 200
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    # In a real environment we might already have the server running. 
    # For this check I'm assuming user might run this against a running server or I start it.
    # I'll just print instructions to run server first if it fails connection.
    try:
        test_endpoints()
    except requests.exceptions.ConnectionError:
        print("CRITICAL: Server is not running. Please run 'python server.py' in another terminal first.")
