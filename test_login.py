import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_login_refinement():
    print("Testing Refined Login Format (admin_<city>_<pincode>)...")

    # Positive Case
    valid_user = "admin_delhi_110001"
    resp = requests.post(f"{BASE_URL}/login", json={"username": valid_user, "password": "admin123"})
    data = resp.json()
    if data['success'] and data['region'] == "Delhi" and data['pincode_scope'] == "110001":
        print(f"✅ Success: {valid_user} -> Region: {data['region']}")
    else:
        print(f"❌ Failed Valid User: {resp.text}")

    # Negative Case (Old Format)
    invalid_user = "admin_delhi"
    resp = requests.post(f"{BASE_URL}/login", json={"username": invalid_user, "password": "admin123"})
    if resp.status_code == 400:
        print("✅ Correctly rejected invalid format 'admin_delhi'")
    else:
        print("❌ Incorrectly accepted invalid format")

if __name__ == "__main__":
    try:
        test_login_refinement()
    except:
        print("Server not running")
