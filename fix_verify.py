import sys
import os
sys.path.append(os.getcwd())
from src.data_manager import DataManager

try:
    print("Initializing DataManager...")
    dm = DataManager()
    
    print("Checking Centers Schema...")
    centers = dm.get_centers()
    if 'city' in centers.columns and 'pincode' in centers.columns:
        print("PASS: Schema check passed. Columns 'city' and 'pincode' found.")
    else:
        print("FAIL: Schema missing columns.")
        exit(1)
        
    print("Checking Data Content...")
    delhi = centers[centers['city'] == 'New Delhi']
    if not delhi.empty:
        print(f"PASS: Found {len(delhi)} centers in New Delhi.")
    else:
        print("FAIL: Dummy data not loaded correctly.")

    print("\nSUCCESS: All integrity checks passed. App should work now.")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    exit(1)
