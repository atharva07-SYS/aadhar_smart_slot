import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_v2():
    print("--- TESTING V2 FEATURES ---")

    # 1. Test Admin Login
    print("\n[TEST] Admin Login")
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"username": "admin_gurugram", "password": "admin123"})
        data = resp.json()
        if data['success'] and data['region'] == "Gurugram":
            print("✅ Login Success (Regional Logic Verified)")
        else:
            print(f"❌ Login Failed: {data}")
    except Exception as e: print(f"❌ Error: {e}")

    # 2. Test V2 Booking (New Fields)
    print("\n[TEST] Booking with V2 Fields")
    req_id = None
    try:
        payload = {
            "name": "Atharva Test",
            "phone": "9876543210",
            "age": "25",
            "request_type": "eKYC",
            "user_type": "Scheduled",
            "city": "Gurugram",
            "pincode": "122002"
        }
        resp = requests.post(f"{BASE_URL}/book_appointment", json=payload)
        data = resp.json()
        if data['success']:
            req_id = data['data']['request_id']
            print(f"✅ Booking Success. Request ID: {req_id}")
        else:
            print(f"❌ Booking Failed: {data}")
    except Exception as e: print(f"❌ Error: {e}")

    # 3. Test Tracking
    print("\n[TEST] Tracking Request")
    if req_id:
        try:
            resp = requests.get(f"{BASE_URL}/track_request?request_id={req_id}")
            data = resp.json()
            if data['success'] and data['data']['name'] == "Atharva Test":
                print("✅ Tracking Success (Name Verified)")
            else:
                print(f"❌ Tracking Failed: {data}")
        except Exception as e: print(f"❌ Error: {e}")
    else:
        print("⚠️ Skipping Tracking Test (No Req ID)")

    # 4. Test Filtered Admin Data
    print("\n[TEST] Admin Data Filter (Region: Gurugram)")
    try:
        payload = {"region": "Gurugram", "status": "All", "age_group": "All"}
        resp = requests.post(f"{BASE_URL}/admin/data", json=payload)
        data = resp.json()
        # Should find at least the one we just booked
        found = any(log['request_id'] == req_id for log in data['logs'])
        if found:
            print("✅ Admin Data Filter Success (Found new booking)")
        else:
            print(f"❌ Admin Data Filter Failed (Booking not in logs). Total Logs: {len(data['logs'])}")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        test_v2()
    except:
        print("Server likely not running.")
