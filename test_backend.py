import sys
import os
sys.path.append(os.getcwd())

from src.backend import CrowdSystemBackend
import datetime

def test_system():
    print("Initializing Backend...")
    be = CrowdSystemBackend()
    
    # Reset for clean test
    be.dm.reset_daily_data()
    
    centers = be.get_all_centers()
    center_id = centers.iloc[0]['center_id']
    center_name = centers.iloc[0]['name']
    print(f"Testing with Center: {center_name} ({center_id})")

    # 1. Test Scheduled Booking
    print("\n--- Test 1: Scheduled Booking ---")
    today = datetime.date.today()
    res = be.process_scheduled_request({"request_type": "New"}, center_id, today, 10)
    if res['success']:
        print("PASS: Scheduled Booking Confirmed")
    else:
        print(f"FAIL: {res['message']}")

    # 2. Test Walk-in
    print("\n--- Test 2: Walk-in Booking ---")
    res_walk = be.process_walkin_request({"request_type": "Update"}, center_id)
    if res_walk['success'] or "closed" in res_walk['message']:
        print(f"PASS: Walk-in handled. Msg: {res_walk['message']}")
    else:
        print(f"FAIL: {res_walk['message']}")

    # 3. Test Load (Simulate Overload)
    print("\n--- Test 3: Overload Simulation ---")
    # Reduces capacity to 1 for testing? No, easier to just fill it up.
    # Be.dm.slots is accessible. Let's artificially fill a slot.
    be.dm.update_slot_load(center_id, today, 12, is_walkin=False)
    # Hack: set booked count to 100 for hour 12
    mask = (be.dm.slots["center_id"] == center_id) & (be.dm.slots["date"] == str(today)) & (be.dm.slots["hour"] == 12)
    idx = be.dm.slots[mask].index[0]
    be.dm.slots.at[idx, "booked_count"] = 100 # Over capacity
    be.dm.save_slots()
    
    # Try book
    res_fail = be.process_scheduled_request({"request_type": "New"}, center_id, today, 12)
    if not res_fail['success'] and "alternatives" in res_fail:
        print("PASS: Overload detected, alternatives suggested.")
        print("Alternatives:", [a['value'] for a in res_fail['alternatives']])
    else:
        print("FAIL: Should have failed due to overload.")

if __name__ == "__main__":
    test_system()
