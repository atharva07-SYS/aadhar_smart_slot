import random
import datetime
from src.backend import CrowdSystemBackend
from src.utils import generate_request_id, get_current_time

# Setup
backend = CrowdSystemBackend()

CITIES = ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"]
PINCODES = {
    "New Delhi": "110001",
    "Mumbai": "400014", 
    "Bengaluru": "560038",
    "Noida": "201301",
    "Ghaziabad": "201002",
    "Gurugram": "122002"
}

NAMES = ["Aarav", "Vihaan", "Aditya", "Sai", "Ishaan", "Diya", "Ananya", "Saanvi", "Aditi", "Priya", "Rahul", "Amit", "Sneha", "Kavita"]
SURNAMES = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Kumar", "Reddy", "Nair", "Iyer"]

SERVICES = ["New Enrollment", "Biometric Update", "Demographic Update", "eKYC"]
STATUSES = ["Confirmed", "Pending", "Completed"]

def seed_data(count=50):
    print(f"Seeding {count} records...")
    
    data_list = []
    
    for _ in range(count):
        city = random.choice(CITIES)
        pincode = PINCODES[city]
        
        # Random User Details
        name = f"{random.choice(NAMES)} {random.choice(SURNAMES)}"
        phone = f"98{random.randint(10000000, 99999999)}"
        age = random.randint(5, 80)
        
        # Determine Age Group (Reuse logic or just string)
        if age < 18: age_group = "Child (0-18)"
        elif age < 60: age_group = "Adult (18-60)"
        else: age_group = "Senior (60+)"
        
        req_type = random.choice(SERVICES)
        
        # Create Request Object
        # We manually inject because we want to fake "past" data too maybe? 
        # Actually easier to just use the backend.process_request but that gives Future slots.
        # Let's manually construct to have some variety in dates.
        
        assigned_date = datetime.date.today() + datetime.timedelta(days=random.randint(0, 5))
        
        booking = {
            "name": name,
            "phone": phone,
            "age": str(age),
            "age_group": age_group,
            "request_type": req_type,
            "user_type": "Scheduled",
            "city": city,
            "pincode": pincode
        }
        
        # Let backend handle slot finding to ensure consistency
        res = backend.process_request(booking)
        
        if res['success']:
            # Manually tweak status for demo variety
            if random.random() < 0.3:
                # Hack: Update the last inserted row to be 'Completed'
                idx = backend.dm.requests.index[-1]
                backend.dm.requests.at[idx, 'status'] = 'Completed'
                
            print(f"Created: {name} in {city}")

    backend.dm.save_requests()
    print("Seeding Complete!")

if __name__ == "__main__":
    seed_data()
