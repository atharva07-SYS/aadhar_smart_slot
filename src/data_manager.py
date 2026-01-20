import pandas as pd
import os
import datetime
from src.utils import get_current_time

DATA_DIR = "data"
CENTERS_FILE = os.path.join(DATA_DIR, "centers.csv")
REQUESTS_FILE = os.path.join(DATA_DIR, "requests.csv")
SLOTS_FILE = os.path.join(DATA_DIR, "slots.csv")

class DataManager:
    def __init__(self):
        self._ensure_data_dir()
        self.centers = self._load_or_create_centers()
        self.requests = self._load_or_create_requests()
        self.slots = self._load_or_create_slots()

    def _ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _load_or_create_centers(self):
        # Always recreate metadata for this refactor to ensure new columns exist
        data = [
            {"center_id": "ASK001", "name": "ASK Delhi - Connaught Place", "city": "New Delhi", "pincode": "110001", "capacity_per_hour": 50},
            {"center_id": "ASK002", "name": "ASK Delhi - Laxmi Nagar", "city": "New Delhi", "pincode": "110092", "capacity_per_hour": 40},
            {"center_id": "ASK003", "name": "ASK Noida - Sector 18", "city": "Noida", "pincode": "201301", "capacity_per_hour": 30},
            {"center_id": "ASK004", "name": "ASK Ghaziabad - Raj Nagar", "city": "Ghaziabad", "pincode": "201002", "capacity_per_hour": 25},
            {"center_id": "ASK005", "name": "ASK Gurugram - Cyber Hub", "city": "Gurugram", "pincode": "122002", "capacity_per_hour": 60},
            {"center_id": "ASK006", "name": "ASK Mumbai - Dadar", "city": "Mumbai", "pincode": "400014", "capacity_per_hour": 80},
            {"center_id": "ASK007", "name": "ASK Mumbai - Andheri", "city": "Mumbai", "pincode": "400053", "capacity_per_hour": 70},
            {"center_id": "ASK008", "name": "ASK Bengaluru - Indiranagar", "city": "Bengaluru", "pincode": "560038", "capacity_per_hour": 45},
        ]
        df = pd.DataFrame(data)
        df.to_csv(CENTERS_FILE, index=False)
        return df

    def _load_or_create_requests(self):
        if os.path.exists(REQUESTS_FILE):
            return pd.read_csv(REQUESTS_FILE)
        columns = ["request_id", "user_type", "input_city", "input_pincode", "request_type", "status", "assigned_center_id", "assigned_date", "assigned_time_slot", "timestamp", "name", "phone", "age", "age_group"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(REQUESTS_FILE, index=False)
        return df

    def _load_or_create_slots(self):
        if os.path.exists(SLOTS_FILE):
            return pd.read_csv(SLOTS_FILE)
        columns = ["center_id", "date", "hour", "booked_count", "walkin_count"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(SLOTS_FILE, index=False)
        return df

    def save_requests(self):
        self.requests.to_csv(REQUESTS_FILE, index=False)

    def save_slots(self):
        self.slots.to_csv(SLOTS_FILE, index=False)

    def get_centers(self):
        return self.centers

    def get_center_by_id(self, center_id):
        return self.centers[self.centers["center_id"] == center_id].iloc[0]

    def add_request(self, request_data):
        new_row = pd.DataFrame([request_data])
        self.requests = pd.concat([self.requests, new_row], ignore_index=True)
        self.save_requests()

    def get_slot_load(self, center_id, date, hour):
        mask = (self.slots["center_id"] == center_id) & \
               (self.slots["date"] == str(date)) & \
               (self.slots["hour"] == int(hour))
        rows = self.slots[mask]
        if rows.empty:
            return 0, 0, 0
        booked = rows.iloc[0]["booked_count"]
        walkin = rows.iloc[0]["walkin_count"]
        return booked, walkin, booked + walkin

    def update_slot_load(self, center_id, date, hour, is_walkin=False):
        date_str = str(date)
        hour = int(hour)
        mask = (self.slots["center_id"] == center_id) & \
               (self.slots["date"] == date_str) & \
               (self.slots["hour"] == hour)
        
        if self.slots[mask].empty:
            new_row = {
                "center_id": center_id,
                "date": date_str,
                "hour": hour,
                "booked_count": 0 if is_walkin else 1,
                "walkin_count": 1 if is_walkin else 0
            }
            self.slots = pd.concat([self.slots, pd.DataFrame([new_row])], ignore_index=True)
        else:
            idx = self.slots[mask].index[0]
            if is_walkin:
                self.slots.at[idx, "walkin_count"] += 1
            else:
                self.slots.at[idx, "booked_count"] += 1
        
        self.save_slots()

    def reset_daily_data(self):
        self.slots = pd.DataFrame(columns=["center_id", "date", "hour", "booked_count", "walkin_count"])
        self.save_slots()
        self.requests = pd.DataFrame(columns=["request_id", "user_type", "input_city", "input_pincode", "request_type", "status", "assigned_center_id", "assigned_date", "assigned_time_slot", "timestamp"])
        self.save_requests()
