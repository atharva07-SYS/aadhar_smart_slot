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

# --- CUSTOM CSS (Glassmorphism & Premium Theme) ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        background-attachment: fixed;
        color: #ffffff;
    }
    
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
    }

    /* Headings */
    h1, h2, h3 {
        color: #f0f0f0 !important;
        font-weight: 600;
    }
    .main_header {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #d4a017, #f6d365);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 30px;
        font-size: 2.5rem;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.07) !important;
        color: #fff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #d4a017 !important;
        box-shadow: 0 0 10px rgba(212, 160, 23, 0.3);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #d4a017 0%, #aa8012 100%);
        color: white;
        border: none;
        border-radius: 8px;
        height: 50px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(212, 160, 23, 0.5);
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-green { background-color: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid #4caf50; }
    .status-orange { background-color: rgba(255, 152, 0, 0.2); color: #ffb74d; border: 1px solid #ff9800; }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
        animation: fadeIn 0.8s ease-out forwards;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND ---
@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# --- HEADER ---
st.markdown("<div class='animate-fade-in'><h1 class='main_header'>UIDAI Aadhaar Appointment & Crowd Management System</h1></div>", unsafe_allow_html=True)

# --- TABS ---
# Custom stylable tabs (Streamlit native tabs are hard to style heavily, keeping default but consistent)
tab_citizen, tab_admin = st.tabs(["👤 Citizen Services", "🔒 Admin Console"])

# ================= CITIZEN TAB =================
with tab_citizen:
    st.markdown("<div class='glass-card animate-fade-in'>", unsafe_allow_html=True)
    menu = st.radio("", ["Book Priority Appointment", "Track Application Status"], horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if menu == "Book Priority Appointment":
        st.markdown("<div class='glass-card animate-fade-in'>", unsafe_allow_html=True)
        st.subheader("📝 New Application")
        st.info("ℹ️ Priority access for online bookings. Walk-ins subject to availability.")

        with st.form("booking_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", placeholder="Enter name as per documents")
                phone = st.text_input("Mobile Number", placeholder="10-digit number", max_chars=10)
                age = st.number_input("Age", min_value=1, max_value=120, step=1)
                
            with c2:
                req_type = st.selectbox("Service Type", ["New Enrollment", "Biometric Update", "Demographic Update", "eKYC"])
                city = st.selectbox("City", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])
                pincode = st.text_input("Pincode", max_chars=6)

            st.write("")
            submitted = st.form_submit_button("Find & Book Slot")

            if submitted:
                if not name or len(phone)!=10 or not pincode:
                    st.error("Please fill all details correctly.")
                else:
                    with st.spinner("🔄 Analyzing Crowd Density & Allocating Slot..."):
                        time.sleep(1.5) # Simulate processing
                        
                        # Process
                        age_group = "Child (0-18)" if age < 18 else "Adult (18-60)" if age < 60 else "Senior (60+)"
                        payload = {
                            "name": name, "phone": phone, "age": str(age), "age_group": age_group,
                            "request_type": req_type, "user_type": "Scheduled",
                            "city": city, "pincode": pincode
                        }
                        result = backend.process_request(payload)
                        
                        if result['success']:
                            d = result['data']
                            st.balloons()
                            st.success("✅ Appointment Confirmed Successfully!")
                            
                            # Digital Ticket UI
                            st.markdown(f"""
                            <div class='glass-card' style='border-left: 5px solid #4caf50;'>
                                <div style='display:flex; justify-content:space-between; align-items:center;'>
                                    <h2>🎫 Digital Token</h2>
                                    <span class='status-badge status-green'>CONFIRMED</span>
                                </div>
                                <hr style='border-color: rgba(255,255,255,0.1);' />
                                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                                    <div><strong>Request ID:</strong> <code style='color:#d4a017'>{d['request_id']}</code></div>
                                    <div><strong>Center:</strong> {result['center_name']}</div>
                                    <div><strong>Date:</strong> {d['assigned_date']}</div>
                                    <div><strong>Time:</strong> {d['assigned_time_slot']}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Slip Content
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
                            
                            st.download_button("⬇️ Download Receipt", receipt_txt, file_name=f"Slip_{d['request_id']}.txt")
                        else:
                            st.error(f"❌ {result['message']}")
        st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Track Application Status":
        st.markdown("<div class='glass-card animate-fade-in'>", unsafe_allow_html=True)
        st.subheader("🔍 Track Application")
        
        c_track1, c_track2 = st.columns([3, 1])
        with c_track1:
            req_id_input = st.text_input("Enter Request ID", placeholder="REQ...")
        with c_track2:
            st.write("")
            st.write("")
            track_btn = st.button("Track Status")

        if track_btn:
            with st.spinner("Searching Database..."):
                time.sleep(1)
                match = backend.dm.requests[backend.dm.requests['request_id'] == req_id_input]
                
            if not match.empty:
                rec = match.iloc[0]
                status_class = "status-green" if "Confirmed" in rec['status'] else "status-orange"
                st.markdown(f"""
                <div class='glass-card' style='margin-top: 20px;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <h3>{rec['name']}</h3>
                        <span class='status-badge {status_class}'>{rec['status']}</span>
                    </div>
                    <p><strong>Appointment:</strong> {rec['assigned_date']} at {rec['assigned_time_slot']}</p>
                    <p style='color: #aaa; font-size: 0.9em;'>Center ID: {rec['assigned_center_id']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠️ Request ID not found in the system.")
        st.markdown("</div>", unsafe_allow_html=True)


# ================= ADMIN TAB =================
with tab_admin:
    
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False
        st.session_state['admin_region'] = None

    if not st.session_state['admin_logged_in']:
        # Login Form
        col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
        with col_login2:
            st.markdown("<div class='glass-card animate-fade-in'>", unsafe_allow_html=True)
            st.subheader("🔐 Secure Admin Portal")
            with st.form("admin_login"):
                u = st.text_input("Username", placeholder="e.g. admin_delhi_110001")
                p = st.text_input("Password", type="password")
                btn = st.form_submit_button("Verify & Login")
                
                if btn:
                    if p == "admin123":
                        parts = u.split('_')
                        if len(parts) >= 3 and parts[0] == 'admin':
                            # --- SECURITY SIMULATION ---
                            msg_placeholder = st.empty()
                            bar = st.progress(0)
                            
                            msg_placeholder.write("🔄 Connecting to UIDAI C-CID Server...")
                            time.sleep(0.8)
                            bar.progress(30)
                            
                            msg_placeholder.write("🔐 Verifying Admin Credentials...")
                            time.sleep(0.8)
                            bar.progress(60)
                            
                            msg_placeholder.write("📡 Syncing Regional Data...")
                            time.sleep(0.8)
                            bar.progress(100)
                            time.sleep(0.5)
                            # ---------------------------

                            st.session_state['admin_logged_in'] = True
                            st.session_state['admin_region'] = parts[1].capitalize()
                            st.rerun()
                        else:
                            st.error("Invalid Username Format. Use admin_<city>_<pincode>")
                    else:
                        st.error("❌ Access Denied: Invalid Password")
            st.caption("Demo Access: admin_delhi_110001 / admin123")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Dashboard
        region = st.session_state['admin_region']
        
        st.markdown(f"""
        <div class='glass-card animate-fade-in' style='display:flex; justify-content:space-between; align-items:center;'>
            <h2>📊 Regional Dashboard: {region}</h2>
            <div style='text-align:right;'>
                <span class='status-badge status-green'>● LIVE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 Secure Logout", key='logout'):
                st.session_state['admin_logged_in'] = False
                st.rerun()

        # Data Filter Logic
        df = backend.dm.requests.copy()
        df = df.fillna('')
        df = df[df['input_city'].str.contains(region, case=False)]
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='glass-card'><h3 style='margin:0'>{len(df)}</h3><p style='color:#ccc'>Total Requests</p></div>", unsafe_allow_html=True)
        with m2:
            today_count = len(df[df['assigned_date'] == str(datetime.date.today())])
            st.markdown(f"<div class='glass-card'><h3 style='margin:0'>{today_count}</h3><p style='color:#ccc'>Scheduled Today</p></div>", unsafe_allow_html=True)
        with m3:
            redirects = len(df[df['status'].str.contains("Rescheduled") | df['status'].str.contains("admin")])
            st.markdown(f"<div class='glass-card'><h3 style='margin:0'>{redirects}</h3><p style='color:#ccc'>System Interventions</p></div>", unsafe_allow_html=True)
        
        # Controls & Table
        st.markdown("<div class='glass-card animate-fade-in'>", unsafe_allow_html=True)
        c_filter1, c_filter2 = st.columns(2)
        with c_filter1:
            f_age = st.selectbox("Filter by Age Group", ["All", "Child (0-18)", "Adult (18-60)", "Senior (60+)"])
        with c_filter2:
            f_status = st.selectbox("Filter by Status", ["All", "Confirmed", "Completed"])
            
        if f_age != "All": df = df[df['age_group'] == f_age]
        if f_status != "All": df = df[df['status'].str.contains(f_status)]
        
        st.dataframe(
            df[['request_id', 'name', 'age_group', 'assigned_date', 'assigned_time_slot', 'status']], 
            hide_index=True, 
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Actions
        st.subheader("⚡ Administrative Actions")
        act1, act2 = st.columns(2)
        
        with act1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.write("### ⚖️ Load Balancing")
            centers = backend.get_all_centers()
            target = st.selectbox("Select Center to Offload", centers['center_id'].tolist(), format_func=lambda x: centers[centers['center_id']==x]['name'].values[0])
            if st.button("Shift Excess Load to Tomorrow"):
                with st.spinner("Re-calculating Schedules..."):
                    time.sleep(1)
                    count = backend.process_admin_redistribution(target)
                st.success(f"✅ Successfully moved {count} appointments to next available slots.")
            st.markdown("</div>", unsafe_allow_html=True)
                
        with act2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.write("### 🚨 Emergency Protocols")
            st.warning("Simulation Tools")
            if st.button("⚠️ Broadcast Outage Alert"):
                st.toast("⚠️ SMS Alert: System Outage Notification Broadcasted to all centers!")
            st.markdown("</div>", unsafe_allow_html=True)
