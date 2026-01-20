from flask import Flask, jsonify, request, send_from_directory
from src.backend import CrowdSystemBackend
import os

app = Flask(__name__, static_folder='static')
backend = CrowdSystemBackend()

# Serve Frontend
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# API Endpoints
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Mock Authentication
    # Format: admin_city_pincode (e.g., admin_delhi_110001)
    if password == "admin123":
        parts = username.split('_')
        if len(parts) >= 3 and parts[0] == 'admin':
            city = parts[1].capitalize()
            pincode = parts[2]
            
            # Region scope is primarily the city, but we pass pincode too if needed
            # For this demo, let's use City as the primary region filter label
            return jsonify({
                'success': True, 
                'token': f'token_{username}', 
                'region': city,
                'pincode_scope': pincode
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid Username Format. Use admin_<city>_<code (e.g. admin_delhi_110001)'}), 400
    else:
        return jsonify({'success': False, 'message': 'Invalid Credentials'}), 401

@app.route('/api/book_appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.json
        # Validate input
        required_fields = ['request_type', 'user_type', 'city', 'pincode', 'name', 'phone', 'age']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing field: {field}'}), 400

        # Determine Age Group
        try:
            age = int(data['age'])
            if age < 18: age_group = "Child (0-18)"
            elif age < 60: age_group = "Adult (18-60)"
            else: age_group = "Senior (60+)"
        except:
             age_group = "Unknown"
        
        data['age_group'] = age_group

        result = backend.process_request(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/track_request', methods=['GET'])
def track_request():
    req_id = request.args.get('request_id')
    if not req_id:
        return jsonify({'success': False, 'message': 'Request ID Required'}), 400
        
    req_df = backend.dm.requests
    match = req_df[req_df['request_id'] == req_id]
    
    if match.empty:
         return jsonify({'success': False, 'message': 'Request ID not found.'}), 404
         
    # Return status details
    record = match.iloc[0].to_dict()
    # Filter sensitive data
    filtered_response = {
        'request_id': record['request_id'],
        'status': record['status'],
        'assigned_center_id': record['assigned_center_id'],
        'assigned_date': record['assigned_date'],
        'assigned_time_slot': record['assigned_time_slot'],
        'name': record['name'] # Verify identity
    }
    return jsonify({'success': True, 'data': filtered_response})

@app.route('/api/centers', methods=['GET'])
def get_centers():
    centers_df = backend.get_all_centers()
    centers_list = centers_df.to_dict(orient='records')
    return jsonify(centers_list)

@app.route('/api/admin/data', methods=['POST'])
def get_admin_data():
    """
    Returns data filtered by admin region and other filters.
    """
    data = request.json
    region = data.get('region', 'All') # User's admin region
    filter_status = data.get('status', 'All')
    filter_age = data.get('age_group', 'All')
    
    req_df = backend.dm.requests.fillna('') # Handle NaNs
    
    # 1. Region Filter (Search in City or Center Name)
    if region != 'All':
        # Simple match: if region string is in city name
        req_df = req_df[req_df['input_city'].str.contains(region, case=False, na=False)]
        
    # 2. Status Filter
    if filter_status == 'Pending':
        req_df = req_df[req_df['status'] == 'Confirmed'] # Confirmed means booked but future (Pending work)
    elif filter_status == 'Done':
        # In this demo, nothing is marked 'Done' yet, but let's simulate
        # Maybe "past dates" could be considered done? 
        # For now, just string match if we had a status 'Completed'
        req_df = req_df[req_df['status'] == 'Completed']
        
    # 3. Age Filter
    if filter_age != 'All':
        req_df = req_df[req_df['age_group'] == filter_age]
        
    # Stats Calculation on Filtered Data
    total_req = len(req_df)
    import datetime
    today_str = str(datetime.date.today())
    today_req = len(req_df[req_df['assigned_date'] == today_str])
    
    overload_redirects = len(req_df[req_df['status'].str.contains("Rescheduled", na=False) | req_df['status'].str.contains("De-congested", na=False)])
    
    # Tables
    logs = req_df.sort_values(by="timestamp", ascending=False).head(50).to_dict(orient='records')
    
    return jsonify({
        'total_req': total_req,
        'today_req': today_req,
        'overload_redirects': overload_redirects,
        'logs': logs
    })

@app.route('/api/admin/redistribute', methods=['POST'])
def redistribute_load():
    data = request.json
    target_center_id = data.get('center_id')
    if not target_center_id:
         return jsonify({'success': False, 'message': 'Missing center_id'}), 400
         
    count = backend.process_admin_redistribution(target_center_id)
    return jsonify({'success': True, 'count': count, 'message': f'{count} appointments shifted to tomorrow.'})

@app.route('/api/reset', methods=['POST'])
def reset_system():
    backend.dm.reset_daily_data()
    return jsonify({'success': True, 'message': 'System data reset successfully.'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
