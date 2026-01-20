import datetime
import random

def get_current_time():
    """Returns simulated current time."""
    return datetime.datetime.now()

def generate_request_id(prefix="REQ"):
    """Generates a random request ID."""
    return f"{prefix}{random.randint(100000, 999999)}"

def format_time_slot(hour):
    """Formats 24h hour integer to readable string."""
    return f"{hour:02d}:00 - {hour+1:02d}:00"

def simulate_sms_content(request_id, center_name, date, time):
    """Generates the text for a simulated SMS."""
    return f"Dear Citizen, your appointment at {center_name} is confirmed for {date} at {time}. Request ID: {request_id}. Please carry your documents. - UIDAI"
