import pandas as pd
import datetime
from src.data_manager import DataManager
from src.utils import generate_request_id, simulate_sms_content, get_current_time

class CrowdSystemBackend:
    def __init__(self):
        self.dm = DataManager()
        self.WALKIN_BUFFER_PERCENT = 0.20 # 20% reserved for walkins

    def get_all_centers(self):
        return self.dm.get_centers()

    def find_best_center(self, city, pincode):
        """
        Locates the best center. Priority:
        1. Exact Pincode Match
        2. Exact City Match
        3. Default to a major hub if not found (Demo logic)
        """
        centers = self.dm.get_centers()
        
        # 1. Pincode Match
        match = centers[centers['pincode'] == str(pincode)]
        if not match.empty:
            return match.iloc[0]
            
        # 2. City Match
        match = centers[centers['city'].str.lower() == city.lower()]
        if not match.empty:
             # Load balancing: Pick one with random/round-robin in real life. Here, pick first.
            return match.iloc[0]
            
        # 3. Fallback
        return centers.iloc[0]

    def allocate_slot_automatically(self, center_id, is_walkin=False):
        """
        Finds the first available slot starting today -> tomorrow -> day after.
        Returns: (date, hour, is_deferred)
        """
        center = self.dm.get_center_by_id(center_id)
        capacity = center['capacity_per_hour']
        max_bookable = int(capacity * (1 - self.WALKIN_BUFFER_PERCENT)) if not is_walkin else capacity
        
        start_date = get_current_time().date()
        hours = range(9, 17) # 9 AM to 5 PM
        
        # Search Horizon: 3 Days
        for day_offset in range(3):
            check_date = start_date + datetime.timedelta(days=day_offset)
            
            for hour in hours:
                # If today, skip past hours
                # In demo, we might want to allow booking for 'now' if it's past? No, strict logic.
                current_time = get_current_time()
                if day_offset == 0 and hour <= current_time.hour and not is_walkin:
                   continue 

                booked, walkin, total = self.dm.get_slot_load(center_id, check_date, hour)
                
                limit = max_bookable
                current_load = booked if not is_walkin else total # Walkins compete with everyone
                
                if current_load < limit:
                    # Found a slot!
                    is_deferred = (day_offset > 0)
                    return check_date, hour, is_deferred
        
        return None, None, True # Totally full

    def process_request(self, user_details):
        """
        Main entry point for Citizen.
        Automatic assignment of Center -> Date -> Time.
        """
        city = user_details['city']
        pincode = user_details['pincode']
        user_type = user_details['user_type'] # 'Scheduled' or 'Walk-in'
        
        # 1. Find Center
        assigned_center = self.find_best_center(city, pincode)
        center_id = assigned_center['center_id']
        center_name = assigned_center['name']
        
        # 2. Allocate Slot
        today = get_current_time().date()
        is_walkin_flow = (user_type == "Walk-in")
        
        assigned_date, assigned_hour, is_deferred = self.allocate_slot_automatically(center_id, is_walkin=is_walkin_flow)
        
        if assigned_date:
            # Book it
            self.dm.update_slot_load(center_id, assigned_date, assigned_hour, is_walkin=is_walkin_flow)
            
            req_id = generate_request_id("REQ")
            status = "Confirmed"
            
            if is_deferred and not is_walkin_flow:
                 status = "De-congested (Next Day)"
            if is_walkin_flow and assigned_date > today:
                 status = "Deferred Walk-in"

            # Log
            req_data = {
                "request_id": req_id,
                "user_type": user_type,
                "input_city": city,
                "input_pincode": pincode,
                "request_type": user_details['request_type'],
                "status": status,
                "assigned_center_id": center_id,
                "assigned_date": str(assigned_date),
                "assigned_time_slot": f"{assigned_hour:02d}:00",
                "timestamp": str(get_current_time())
            }
            self.dm.add_request(req_data)
            
            sms = simulate_sms_content(req_id, center_name, str(assigned_date), f"{assigned_hour:02d}:00")
            
            return {
                "success": True,
                "data": req_data,
                "center_name": center_name,
                "message": sms
            }
        else:
            return {
                "success": False,
                "message": "System Overload. All nearby centers are full for the next 3 days. Please try again later."
            }

    def process_admin_redistribution(self, from_center_id):
        """
        Admin Tool: Shift excess load from one center to others or future dates.
        Simplification: Just finds 'Scheduled' people for Today and moves them to Tomorrow.
        """
        today = str(get_current_time().date())
        # Find victims
        mask = (self.dm.requests["assigned_center_id"] == from_center_id) & \
               (self.dm.requests["assigned_date"] == today) & \
               (self.dm.requests["status"] == "Confirmed")
        
        affected_indices = self.dm.requests[mask].index
        count = 0
        
        tomorrow = str(get_current_time().date() + datetime.timedelta(days=1))
        
        for idx in affected_indices:
            # Move to tomorrow same time (naive)
            self.dm.requests.at[idx, "assigned_date"] = tomorrow
            self.dm.requests.at[idx, "status"] = "Rescheduled (Admin)"
            count += 1
            
        self.dm.save_requests()
        return count
