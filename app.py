import streamlit as st
import pandas as pd
import time
import datetime
import plotly.express as px  # For professional charts
from src.backend import CrowdSystemBackend

# --- CONFIG ---
st.set_page_config(
    page_title="Citizen Service Portal | UIDAI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (Official Light Theme) ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #ecf0f3; /* Light Professional Gray */
        color: #0b1e47;
    }
    
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    /* Professional White Cards */
    .prof-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border-top: 5px solid #f3a12f; /* Aadhaar Gold */
        margin-bottom: 25px;
        transition: transform 0.2s ease;
    }
    .prof-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* Headings */
    h1, h2, h3 {
        color: #0b1e47 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-title {
        color: #0b1e47;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-top: 20px;
    }
    .sub-title {
        color: #7b8a8b;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #f3a12f; /* Gold */
        color: #0b1e47;
        border: none;
        border-radius: 6px;
        height: 48px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #d48e2a;
        color: #fff;
    }

    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 6px !important;
        height: 45px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0b1e47 !important;
        box-shadow: none;
    }

    /* Notifications */
    .notification-box {
        padding: 15px;
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        color: #1b5e20;
        font-weight: 500;
        margin-top: 10px;
        border-radius: 4px;
    }
    
    /* Metrics */
    .metric-container {
        text-align: center;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #eee;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0b1e47;
    }
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND ---
@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# --- HEADER LOGO & TITLE ---
# Using a text representation for logo place to keep it clean if image not available, 
# but styling it like the header in the image.
c1, c2 = st.columns([1, 10])
with c1:
    st.markdown("<h1>☀️</h1>", unsafe_allow_html=True) # Placeholder for Aadhaar Logo
with c2:
    st.markdown("<div style='text-align:right; font-weight:bold; color:#0b1e47; padding-top:20px;'>Citizen Service Portal</div>", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Book Your Aadhaar Appointment</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Skip the queue. Secure your slot now with our smart scheduling system.</p>", unsafe_allow_html=True)

# --- TABS ---
# To keep professional look, we use invisible tabs or custom switcher? 
# Standard tabs are fine if styled, but let's stick to the separation required.
tab_citizen, tab_admin = st.tabs(["🏛️ Citizen Services", "⚙️ Admin Dashboard"])

# ================= CITIZEN PORTAL =================
with tab_citizen:
    
    col_left, col_right = st.columns([1.5, 1])
    
    # --- LEFT: APPLICATION FORM ---
    with col_left:
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.write("### 📋 Applicant Details")
        st.markdown("---")
        
        with st.form("booking_form"):
            name = st.text_input("Full Name", placeholder="Enter Full Name as per documents")
            
            fc1, fc2 = st.columns(2)
            with fc1:
                phone = st.text_input("Mobile Number", placeholder="10-digit Mobile", max_chars=10)
                age = st.number_input("Age", min_value=1, max_value=120, step=1)
            with fc2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                req_type = st.selectbox("Service Type", ["New Enrollment", "Biometric Update", "Demographic Update", "eKYC"])

            st.write("###### 📍 Location Preferences")
            lc1, lc2 = st.columns(2)
            with lc1:
                city = st.selectbox("Select City", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])
            with lc2:
                pincode = st.text_input("Pincode", placeholder="e.g. 110001", max_chars=6)

            st.write("")
            submitted = st.form_submit_button("Find & Book Slot")
            
            if submitted:
                if not name or len(phone)!=10 or not pincode:
                    st.error("Please fill all mandatory fields correctly.")
                else:
                    with st.spinner("Checking Availability & Reserving Slot..."):
                        time.sleep(1.5)
                        age_group = "Child (0-18)" if age < 18 else "Adult (18-60)" if age < 60 else "Senior (60+)"
                        payload = {
                            "name": name, "phone": phone, "age": str(age), "age_group": age_group,
                            "request_type": req_type, "user_type": "Scheduled",
                            "city": city, "pincode": pincode
                        }
                        result = backend.process_request(payload)

                        if result['success']:
                            d = result['data']
                            st.success("Slot Confirmed!")
                            st.markdown(f"""
                            <div class='notification-box'>
                                ✅ SMS Sent to {phone}: "Your appointment is confirmed at {result['center_name']} for {d['assigned_date']} @ {d['assigned_time_slot']}."
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Ticket UI
                            st.info(f"**Request ID:** {d['request_id']} | **Center:** {result['center_name']}")
                        else:
                            st.error(result['message'])
        st.markdown("</div>", unsafe_allow_html=True)

    # --- RIGHT: TRACKING & INFO ---
    with col_right:
        # Track Application
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        st.write("### 🔍 Track Application")
        st.markdown("---")
        track_id = st.text_input("Enter Request ID (e.g. REQ123...)", key="track_input")
        if st.button("TRACK STATUS"):
            match = backend.dm.requests[backend.dm.requests['request_id'] == track_id]
            if not match.empty:
                rec = match.iloc[0]
                status_color = "#2e7d32" if "Confirmed" in rec['status'] else "#ef6c00";
                st.markdown(f"""
                <div style='background:#f1f8e9; padding:15px; border-radius:8px; border-left:4px solid {status_color}'>
                    <h4 style='margin:0; color:{status_color}'>{rec['status']}</h4>
                    <p style='margin:5px 0 0 0;'><strong>Name:</strong> {rec['name']}</p>
                    <p style='margin:0;'><strong>Date:</strong> {rec['assigned_date']}</p>
                    <p style='margin:0;'><strong>Center:</strong> {rec['assigned_center_id']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("No record found for this ID.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Information / Helper
        st.markdown("<div class='prof-card' style='background:#0b1e47; color:white;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:white !important;'>ℹ️ Required Documents</h3>", unsafe_allow_html=True)
        st.markdown("""
        <ul style='padding-left:20px; line-height:1.6;'>
            <li>POI (Proof of Identity)</li>
            <li>POA (Proof of Address)</li>
            <li>POR (Proof of Relationship)</li>
            <li>DOB (Date of Birth) Proof</li>
        </ul>
        <small style='color:#ccc;'>Ensure you carry original copies.</small>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ================= ADMIN DASHBOARD =================
with tab_admin:
    
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False
        st.session_state['admin_region'] = None
        st.session_state['admin_pincode'] = None

    if not st.session_state['admin_logged_in']:
        # Professional Login
        lc1, lc2, lc3 = st.columns([1, 1, 1])
        with lc2:
            st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
            st.write("### 🔐 Admin Secure Login")
            st.markdown("---")
            with st.form("admin_verify"):
                u = st.text_input("Admin ID", placeholder="admin_city_pincode")
                p = st.text_input("Secure Key", type="password")
                verify_btn = st.form_submit_button("VERIFY & ACCESS")
                
                if verify_btn:
                    if p == "admin123":
                        parts = u.split('_')
                        if len(parts) >= 3 and parts[0] == 'admin':
                            city = parts[1].capitalize()
                            pincode = parts[2]
                            
                            with st.status("Verifying Credentials..."):
                                st.write("✅ C-CID Handshake...")
                                time.sleep(0.5)
                                st.write(f"✅ Retrieving Data for Region: {city} ({pincode})...")
                                time.sleep(0.8)
                                st.write("✅ Access Granted.")
                                time.sleep(0.5)
                            
                            st.session_state['admin_logged_in'] = True
                            st.session_state['admin_region'] = city
                            st.session_state['admin_pincode'] = pincode
                            st.rerun()
                        else:
                            st.error("Invalid Format. Use: admin_<city>_<pincode>")
                    else:
                        st.error("Unauthorized Access.")
            st.caption("Demo: admin_delhi_110001 (Pass: admin123)")
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        # LOGGED IN DASHBOARD
        city = st.session_state['admin_region']
        pin = st.session_state['admin_pincode']
        
        # Header with Logout
        h1, h2 = st.columns([4, 1])
        with h1:
            st.markdown(f"<h2>⚙️ Regional Dashboard: {city} ({pin})</h2>", unsafe_allow_html=True)
        with h2:
            if st.button("LOGOUT"):
                st.session_state['admin_logged_in'] = False
                st.rerun()
        
        # --- DATA SCOPING ---
        df = backend.dm.requests.copy()
        df = df.fillna('')
        
        # STRICT FILTER: Show Only if Pincode matches OR City matches (simulating region scope)
        # For stricter demo, let's match exact Pincode if available, else City
        scope_df = df[
            (df['input_pincode'] == pin) | 
            (df['input_city'].str.lower() == city.lower())
        ]
        
        # --- TOP METRICS ---
        st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.markdown(f"<div class='metric-container'><div class='metric-value'>{len(scope_df)}</div><div class='metric-label'>Total Requests</div></div>", unsafe_allow_html=True)
        with m2:
            today_count = len(scope_df[scope_df['assigned_date'] == str(datetime.date.today())])
            st.markdown(f"<div class='metric-container'><div class='metric-value'>{today_count}</div><div class='metric-label'>Today's Load</div></div>", unsafe_allow_html=True)
        with m3:
            pending = len(scope_df[scope_df['status'].str.contains("Confirmed")])
            st.markdown(f"<div class='metric-container'><div class='metric-value' style='color:#f3a12f'>{pending}</div><div class='metric-label'>Pending</div></div>", unsafe_allow_html=True)
        with m4:
            completed = len(scope_df[scope_df['status'].str.contains("Completed")])
            st.markdown(f"<div class='metric-container'><div class='metric-value' style='color:#2e7d32'>{completed}</div><div class='metric-label'>Completed</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- ADVANCED ANALYTICS TABS ---
        t_overview, t_demo, t_slots, t_ops = st.tabs(["Overview List", "Demographics", "Slot Usage", "Operations"])
        
        with t_overview:
            st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
            st.write("#### 📜 Applicant Records")
            
            # Filters
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                f_type = st.selectbox("Service Type", ["All"] + list(scope_df['request_type'].unique()))
            with fc2:
                f_date = st.date_input("Filter Date", value=None)
            with fc3:
                f_stat = st.selectbox("Status", ["All", "Confirmed", "Rescheduled", "Completed"])
            
            # Apply Filters
            view_df = scope_df
            if f_type != "All": view_df = view_df[view_df['request_type'] == f_type]
            if f_date: view_df = view_df[view_df['assigned_date'] == str(f_date)]
            if f_stat != "All": view_df = view_df[view_df['status'].str.contains(f_stat)]
            
            st.dataframe(
                view_df[['request_id', 'name', 'phone', 'age_group', 'request_type', 'assigned_date', 'assigned_time_slot', 'status']],
                use_container_width=True,
                hide_index=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
        with t_demo:
            st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
            st.write("#### 👥 Age & Service Demographics")
            
            # Charts
            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                if not scope_df.empty:
                    df_age = scope_df['age_group'].value_counts().reset_index()
                    df_age.columns = ['Age Group', 'Count']
                    st.bar_chart(df_age.set_index('Age Group'))
                else:
                    st.info("No data for charts")
            with c_chart2:
                if not scope_df.empty:
                    df_req = scope_df['request_type'].value_counts().reset_index()
                    df_req.columns = ['Service', 'Count']
                    st.write("Service Distribution")
                    st.dataframe(df_req, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with t_ops:
            st.markdown("<div class='prof-card'>", unsafe_allow_html=True)
            st.write("#### 📢 Center Operations & Simulation")
            
            col_ops1, col_ops2 = st.columns(2)
            with col_ops1:
                st.info("⚠️ **Trigger System Outage**")
                st.write("Simulate a connectivity failure in this region. This will trigger SMS alerts to all scheduled citizens.")
                if st.button("🚨 TRIGGER OUTAGE & NOTIFY"):
                    st.toast("⚠️ SMS BROADCASTED: 'System Outage at Center. Please wait for reschedule.'")
                    st.error("System status set to: OFFLINE")
            
            with col_ops2:
                 st.success("📨 **Manual SMS Push**")
                 st.write("Send manual reminders for tomorrow's appointments.")
                 if st.button("📤 SEND REMINDERS"):
                     st.toast("✅ 24 SMS Reminders Sent Successfully.")
            st.markdown("</div>", unsafe_allow_html=True)
