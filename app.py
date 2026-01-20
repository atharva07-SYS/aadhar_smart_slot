import streamlit as st
import pandas as pd
import time
from src.backend import CrowdSystemBackend

# Configure Page
st.set_page_config(
    page_title="UIDAI | Aadhaar Seva Kendra",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Government Look
st.markdown("""
    <style>
    .main_header {
        font-family: 'Arial', sans-serif;
        color: #003366;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #28a745;
        color: white;
        border-radius: 5px;
        height: 50px;
        font-size: 18px;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0056b3;
    }
    .highlight {
        font-weight: bold;
        color: #003366;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# Header
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("<h1 class='main_header'>UIDAI Aadhaar Appointment & Crowd Management System</h1>", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=120)
    st.markdown("### Official Portal")
    menu = st.radio("Navigate", ["Citizen Services", "Admin Dashboard"])
    
    st.markdown("---")
    st.markdown("### System Status")
    st.info("System Online\nLoad Auto-Balancing: ACTIVE")
    
    if st.button("Reset System Data"):
        backend.dm.reset_daily_data()
        st.success("Data Reset Complete")

# --- CITIZEN SERVICES ---
if menu == "Citizen Services":
    st.markdown("### 📝 Book an Appointment")
    st.write("Please provide your location details. The system will automatically check crowd density and assign the best available center and time slot.")
    
    with st.container():
        col_form, col_info = st.columns([1, 1])
        
        with col_form:
            with st.form("citizen_form"):
                request_type = st.selectbox("Select Service Type", 
                    ["New Enrollment", "Biometric Update", "Demographic Update", "eKYC"])
                
                user_type = st.radio("Application Category", ["Scheduled", "Walk-in"])
                
                city = st.selectbox("Select City", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])
                pincode = st.text_input("Enter Pincode", max_chars=6, help="e.g. 110001")
                
                submitted = st.form_submit_button("Find & Book Slot")
                
        with col_info:
            if submitted:
                if not pincode or len(pincode) != 6:
                    st.error("Please enter a valid 6-digit Pincode.")
                else:
                    with st.spinner("Analyzing Crowd Density & Finding Best Slot..."):
                        time.sleep(1) # Simulated delay for "processing"
                        
                        user_details = {
                            "request_type": request_type,
                            "user_type": user_type,
                            "city": city,
                            "pincode": pincode
                        }
                        
                        result = backend.process_request(user_details)
                        
                        if result['success']:
                            # Success Card
                            data = result['data']
                            st.balloons()
                            st.markdown(f"""
                            <div class='info-box'>
                                <h3>✅ Appointment Confirmed</h3>
                                <p><b>Request ID:</b> {data['request_id']}</p>
                                <p><b>Assigned Center:</b> <span class='highlight'>{result['center_name']}</span></p>
                                <hr>
                                <h4>📅 {data['assigned_date']} &nbsp;&nbsp; ⏰ {data['assigned_time_slot']}</h4>
                                <hr>
                                <p><i>{result['message']}</i></p>
                                <p><b>Status:</b> {data['status']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(result['message'])
            else:
                st.markdown("""
                <div class='info-box'>
                <h4>Instructions</h4>
                <ol>
                <li>Select the service you need.</li>
                <li>Enter your current City and Pincode.</li>
                <li>The AI System will allocate the guaranteed slot.</li>
                </ol>
                <p><b>Note:</b> Walk-ins are accepted but priority is given to scheduled slots.</p>
                </div>
                """, unsafe_allow_html=True)

# --- ADMIN DASHBOARD ---
if menu == "Admin Dashboard":
    st.markdown("### 📊 Real-time Crowd Control Dashboard")
    
    # Metrics
    req_df = backend.dm.requests
    total_req = len(req_df)
    today_req = len(req_df[req_df['assigned_date'] == str(datetime.date.today())])
    overload_redirects = len(req_df[req_df['status'].str.contains("Rescheduled") | req_df['status'].str.contains("De-congested")])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Requests", total_req)
    m2.metric("Today's Appointments", today_req)
    m3.metric("System-Driven Redirects", overload_redirects, delta_color="inverse")
    
    st.divider()
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("Live Load by City")
        if not req_df.empty:
            city_counts = req_df['input_city'].value_counts()
            st.bar_chart(city_counts)
        else:
            st.info("No data yet.")
            
    with col_b:
        st.subheader("Center Health")
        centers = backend.get_all_centers()
        st.dataframe(centers[["name", "city", "capacity_per_hour"]], hide_index=True)

    st.divider()
    st.subheader("🚨 Crowd Control Actions")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Load Redistribution**")
        target_center = st.selectbox("Select Center to De-congest", centers['center_id'].tolist(), format_func=lambda x: centers[centers['center_id']==x]['name'].values[0])
        if st.button("Shift Excess Load to Next Day"):
            count = backend.process_admin_redistribution(target_center)
            st.warning(f"ACTION COMPLETE: {count} appointments shifted to tomorrow.")
            
    with c2:
        st.markdown("**Simulate Failure**")
        if st.button("TRIGGER NETWORK OUTAGE (Simulated)"):
            st.error("NETWORK FAILURE LOGGED. Automated SMS sent to all affected users.")
            
    st.divider()
    st.subheader("Recent System Logs")
    if not req_df.empty:
        st.dataframe(req_df.sort_values(by="timestamp", ascending=False).head(10))
