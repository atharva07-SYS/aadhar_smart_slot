import streamlit as st
import pandas as pd
import time
import datetime
from src.backend import CrowdSystemBackend

# --- CONFIG ---
st.set_page_config(
    page_title="UIDAI | Aadhaar Service Portal",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main_header {
        font-family: 'Outfit', sans-serif;
        color: #0b1e47;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #d4a017;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #0b1e47;
        color: white;
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #d4a017;
        color: white;
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-confirm { background-color: #e8f5e9; color: #1b5e20; }
    .status-pending { background-color: #fff3e0; color: #e65100; }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND ---
@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# --- HEADER ---
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("<h1 class='main_header'>UIDAI Aadhaar Appointment & Crowd Management System</h1>", unsafe_allow_html=True)

# --- TABS ---
tab_citizen, tab_admin = st.tabs(["👤 Citizen Services", "🔒 Admin Console"])

# ================= CITIZEN TAB =================
with tab_citizen:
    menu = st.radio("Select Action", ["Book Appointment", "Track Status"], horizontal=True)
    
    st.divider()

    if menu == "Book Appointment":
        st.subheader("📝 Book a Priority Appointment")
        st.info("Walk-ins are accepted, but online booking guarantees your slot.")

        with st.form("booking_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", placeholder="As per documents")
                phone = st.text_input("Mobile Number", placeholder="10-digit number", max_chars=10)
                age = st.number_input("Age", min_value=1, max_value=120, step=1)
                
            with c2:
                req_type = st.selectbox("Service Type", ["New Enrollment", "Biometric Update", "Demographic Update", "eKYC"])
                city = st.selectbox("City", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])
                pincode = st.text_input("Pincode", max_chars=6)

            submitted = st.form_submit_button("Find & Book Slot")

            if submitted:
                if not name or len(phone)!=10 or not pincode:
                    st.error("Please fill all details correctly.")
                else:
                    with st.spinner("Analyzing Crowd Density..."):
                        time.sleep(1)
                        # Process
                        age_group = "Child (0-18)" if age < 18 else "Adult (18-60)" if age < 60 else "Senior (60+)"
                        payload = {
                            "name": name, "phone": phone, "age": str(age), "age_group": age_group,
                            "request_type": req_type, "user_type": "Scheduled", # Hidden/Default
                            "city": city, "pincode": pincode
                        }
                        result = backend.process_request(payload)
                        
                        if result['success']:
                            d = result['data']
                            st.success("Appointment Confirmed!")
                            
                            # Receipt Card
                            with st.container():
                                st.markdown(f"""
                                ### ✅ Booking Summary
                                **Request ID:** `{d['request_id']}`  
                                **Center:** {result['center_name']}  
                                **Date:** {d['assigned_date']} | **Time:** {d['assigned_time_slot']}
                                """)
                                
                                # Receipt Text
                                receipt_txt = f"""UIDAI APPOINTMENT SLIP
----------------------
Request ID : {d['request_id']}
Name       : {name}
Phone      : {phone}
Center     : {result['center_name']}
Date       : {d['assigned_date']}
Time       : {d['assigned_time_slot']}
Status     : {d['status']}
----------------------
Please carry original documents."""
                                
                                st.download_button("⬇️ Download Slip", receipt_txt, file_name=f"Slip_{d['request_id']}.txt")
                                st.toast(f"SMS Sent to {phone}")

                        else:
                            st.error(result['message'])

    elif menu == "Track Status":
        st.subheader("🔍 Track Application")
        req_id_input = st.text_input("Enter Request ID (e.g. REQ...)")
        if st.button("Track"):
            match = backend.dm.requests[backend.dm.requests['request_id'] == req_id_input]
            if not match.empty:
                rec = match.iloc[0]
                box_color = "green" if "Confirmed" in rec['status'] else "orange"
                st.markdown(f"""
                <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; border-left: 5px solid {box_color};">
                    <h3>{rec['name']}</h3>
                    <p><strong>Status:</strong> {rec['status']}</p>
                    <p><strong>Date:</strong> {rec['assigned_date']} @ {rec['assigned_time_slot']}</p>
                    <p><small>Center ID: {rec['assigned_center_id']}</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Request ID not found.")


# ================= ADMIN TAB =================
with tab_admin:
    
    # Init Session State
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False
        st.session_state['admin_region'] = None

    if not st.session_state['admin_logged_in']:
        # Login Form
        st.subheader("🔑 Secure Admin Login")
        with st.form("admin_login"):
            u = st.text_input("Username", placeholder="e.g. admin_delhi_110001")
            p = st.text_input("Password", type="password")
            btn = st.form_submit_button("Login")
            
            if btn:
                if p == "admin123":
                    parts = u.split('_')
                    if len(parts) >= 3 and parts[0] == 'admin':
                        st.session_state['admin_logged_in'] = True
                        st.session_state['admin_region'] = parts[1].capitalize()
                        st.rerun()
                    else:
                        st.error("Invalid Username Format. Use admin_<city>_<pincode>")
                else:
                    st.error("Invalid Password")
        st.caption("Demo: admin_delhi_110001 / admin123")

    else:
        # Dashboard
        region = st.session_state['admin_region']
        st.subheader(f"📊 Dashboard - Region: {region}")
        
        if st.button("Logout"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

        # Data Filter Logic
        df = backend.dm.requests.copy()
        df = df.fillna('')
        
        # Region Filter
        df = df[df['input_city'].str.contains(region, case=False)]
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Requests", len(df))
        today_df = df[df['assigned_date'] == str(datetime.date.today())]
        m2.metric("Scheduled Today", len(today_df))
        redirects = len(df[df['status'].str.contains("Rescheduled") | df['status'].str.contains("admin")])
        m3.metric("System Actions", redirects)
        
        st.divider()
        
        # Filters & Table
        c_filter1, c_filter2 = st.columns(2)
        with c_filter1:
            f_age = st.selectbox("Filter Age Group", ["All", "Child (0-18)", "Adult (18-60)", "Senior (60+)"])
        with c_filter2:
            f_status = st.selectbox("Filter Status", ["All", "Confirmed", "Completed"])
            
        if f_age != "All": df = df[df['age_group'] == f_age]
        if f_status != "All": df = df[df['status'].str.contains(f_status)]
        
        st.dataframe(df[['request_id', 'name', 'age_group', 'assigned_date', 'assigned_time_slot', 'status']], hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Actions
        st.subheader("⚡ Quick Actions")
        act1, act2 = st.columns(2)
        
        with act1:
            centers = backend.get_all_centers()
            # Filter dropdown if needed, but for redistribution we might want all
            target = st.selectbox("Redistribute Load From", centers['center_id'].tolist(), format_func=lambda x: centers[centers['center_id']==x]['name'].values[0])
            if st.button("Shift Excess Load"):
                count = backend.process_admin_redistribution(target)
                st.success(f"{count} appointments moved to tomorrow.")
                
        with act2:
            st.warning("Simulation Tools")
            if st.button("Trigger Outage Alert"):
                st.toast("⚠️ SMS Alert Broadcasted to all centers!")

