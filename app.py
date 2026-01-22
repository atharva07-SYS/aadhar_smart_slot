import streamlit as st
import pandas as pd
import time
import datetime
import plotly.express as px
from src.backend import CrowdSystemBackend

# --- CONFIG ---
st.set_page_config(
    page_title="Citizen Service Portal | UIDAI",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (V3 Modern Clean) ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #f4f6f8; /* Soft Cloud Gray */
        color: #1a202c;
    }
    
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Modern Cards */
    .modern-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.03), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(0,0,0,0.02);
        margin-bottom: 24px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
    }

    /* Headings */
    h1, h2, h3 {
        color: #0b1e47;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0b1e47 0%, #1a3675 100%);
        color: white;
        border: none;
        border-radius: 10px;
        height: 50px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 6px rgba(11, 30, 71, 0.15);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1a3675 0%, #0b1e47 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 10px rgba(11, 30, 71, 0.25);
    }
    
    /* Secondary Action Button (Gold) */
    .gold-btn {
        background-color: #f3a12f !important;
        color: #0b1e47 !important;
    }

    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #ffffff !important;
        color: #1a202c !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        height: 48px;
        padding-left: 15px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0b1e47 !important;
        box-shadow: 0 0 0 3px rgba(11, 30, 71, 0.1);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f1f1f1;
    }
    
    /* Metrics */
    .stat-box {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #eff0f6;
        text-align: center;
    }
    .stat-label { color: #6e7c89; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-val { color: #0b1e47; font-size: 2.2rem; font-weight: 800; margin: 5px 0; }
    
    </style>
""", unsafe_allow_html=True)

# --- BACKEND ---
@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# ================= NAVIGATION =================
# If Admin Logged In, show full sidebar Dashboard.
# If Not, show Citizen Portal standard view.

if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
    st.session_state['admin_region'] = None

# --- ADMIN VIEW ---
if st.session_state['admin_logged_in']:
    region = st.session_state['admin_region']
    
    # Sidebar Navigation
    with st.sidebar:
        st.write("### ⚙️ Admin Console")
        st.info(f"📍 **{region}**")
        nav_opt = st.radio("Navigation", ["📊 Dashboard", "📅 Schedules", "👥 Demographics", "🏗️ Operations"], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

    # --- DASHBOARD HEADER ---
    st.title(f"{nav_opt}")
    st.write(f"Real-time data for **{region}**")
    st.markdown("---")
    
    # Filter Scope
    df = backend.dm.requests.copy().fillna('')
    # Strict fake scoping for demo using string match
    scope_df = df[df['input_city'].str.contains(region, case=False) | (df['input_pincode'] == st.session_state.get('admin_pincode', '000000'))]

    if nav_opt == "📊 Dashboard":
        # KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='stat-box'><div class='stat-label'>Total Requests</div><div class='stat-val'>{len(scope_df)}</div></div>", unsafe_allow_html=True)
        with c2:
            today_count = len(scope_df[scope_df['assigned_date'] == str(datetime.date.today())])
            st.markdown(f"<div class='stat-box'><div class='stat-label'>Today's Appointments</div><div class='stat-val'>{today_count}</div></div>", unsafe_allow_html=True)
        with c3:
            pending = len(scope_df[scope_df['status'].str.contains("Confirmed")])
            st.markdown(f"<div class='stat-box'><div class='stat-label'>Pending</div><div class='stat-val' style='color:#f59e0b'>{pending}</div></div>", unsafe_allow_html=True)
        with c4:
            done = len(scope_df[scope_df['status'].str.contains("Completed")])
            st.markdown(f"<div class='stat-box'><div class='stat-label'>Processed</div><div class='stat-val' style='color:#10b981'>{done}</div></div>", unsafe_allow_html=True)

        st.write("")
        st.subheader("📌 Recent Activity")
        st.dataframe(scope_df[['request_id', 'name', 'phone', 'assigned_date', 'status']].tail(10), use_container_width=True, hide_index=True)

    elif nav_opt == "📅 Schedules":
        st.subheader("Manage Appointments")
        
        c_fill1, c_fill2 = st.columns(2)
        with c_fill1:
            sel_date = st.date_input("Select Date", value=datetime.date.today())
        with c_fill2:
            st.write("") # Spacer
            if st.button("Print Manifest"):
                st.toast("Generating PDF Manifest...")

        view_df = scope_df[scope_df['assigned_date'] == str(sel_date)]
        
        if view_df.empty:
            st.info("No appointments scheduled for this date.")
        else:
            st.dataframe(view_df[['assigned_time_slot', 'request_id', 'name', 'request_type', 'status']], use_container_width=True, hide_index=True)

    elif nav_opt == "👥 Demographics":
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
            st.write("**Age Distribution**")
            if not scope_df.empty:
                fig = px.pie(scope_df, names='age_group', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
            st.write("**Service Types**")
            if not scope_df.empty:
                fig2 = px.bar(scope_df, x='request_type', color='request_type')
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif nav_opt == "🏗️ Operations":
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
            st.write("#### 🚨 Emergency Controls")
            st.write("Simulate system outages or crowd surges.")
            if st.button("TRIGGER SERVER OUTAGE"):
                with st.spinner("Broadcasting Alerts..."):
                    time.sleep(2)
                st.error("System Status: OUTAGE. SMS Alerts Sent.")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
            st.write("#### 📢 Communications")
            st.write("Send manual notifications to scheduled citizens.")
            msg = st.text_input("Message Content", "Please arrive 15 mins early.")
            if st.button("Send Broadcast"):
                st.toast(f"Sent: {msg}")
            st.markdown("</div>", unsafe_allow_html=True)


# --- CITIZEN VIEW (Default) ---
else:
    # Sidebar for Citizen too? Maybe just for Admin Toggle
    with st.sidebar:
        st.write("### ☀️ Citizen Portal")
        st.write("Welcome to the Next-Gen Aadhaar Appointment System.")
        st.markdown("---")
        mode = st.radio("Connect As", ["Citizen", "Admin"])
        
        if mode == "Admin":
            st.markdown("---")
            st.subheader("Admin Login")
            with st.form("sidebar_login"):
                u = st.text_input("ID")
                p = st.text_input("Key", type="password")
                if st.form_submit_button("Login"):
                    if p == "admin123" and u.startswith("admin_"):
                        parts = u.split('_')
                        st.session_state['admin_logged_in'] = True
                        st.session_state['admin_region'] = parts[1].capitalize()
                        try:
                            st.session_state['admin_pincode'] = parts[2]
                        except:
                            st.session_state['admin_pincode'] = "000000"
                        st.rerun()
                    else:
                        st.error("Invalid Credentials. Use admin_city_pincode")
            st.caption("Demo: admin_delhi_110001 (admin123)")

    if not st.session_state['admin_logged_in']:
        # MAIN LANDING
        st.markdown("<div style='text-align:center; padding: 40px 0;'>", unsafe_allow_html=True)
        st.title("Book Your Aadhaar Appointment")
        st.write("Skip the queue. Secure your slot with our smart AI scheduling.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Central Container
        col_main, _ = st.columns([1, 0.01]) # Centered feel
        
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
        st.write("### 📝 Application Details")
        st.markdown("---")
        
        with st.form("main_booking"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", placeholder="As per documents")
                phone = st.text_input("Mobile Number", placeholder="10-digit")
                city = st.selectbox("Location", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])

            with c2:
                age = st.number_input("Age", 1, 120)
                req_type = st.selectbox("Service", ["New Enrollment", "Biometric Update", "Demographic Update", "eKYC"])
                pincode = st.text_input("Pincode", placeholder="e.g. 110001")
            
            st.write("")
            btn_col1, btn_col2 = st.columns([1, 2])
            with btn_col2:
                submitted = st.form_submit_button("Find & Book Priority Slot")
            
        if submitted:
            if not name or len(phone)!=10:
                st.error("Please provide valid details.")
            else:
                with st.spinner("🤖 AI Finding Best Slot..."):
                    time.sleep(1.5)
                    age_group = "Child (0-18)" if age < 18 else "Adult (18-60)" if age < 60 else "Senior (60+)"
                    payload = {"name": name, "phone": phone, "age": str(age), "age_group": age_group, "request_type": req_type, "user_type": "Scheduled", "city": city, "pincode": pincode}
                    
                    res = backend.process_request(payload)
                    if res['success']:
                        d = res['data']
                        st.balloons()
                        st.success("✅ Appointment Confirmed!")
                         # Success Card
                        st.markdown(f"""
                        <div style='background:#f0fff4; padding:20px; border-radius:10px; border:1px solid #bbf7d0; margin-top:20px;'>
                            <h3 style='color:#15803d; margin:0;'>Booking ID: {d['request_id']}</h3>
                            <p><strong>Center:</strong> {res['center_name']}</p>
                            <p><strong>Time:</strong> {d['assigned_date']} @ {d['assigned_time_slot']}</p>
                            <small>SMS sent to {phone}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(res['message'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Track Section (Expander)
        with st.expander("🔍 Already applied? Track Status"):
             t_id = st.text_input("Enter Request ID")
             if st.button("Track"):
                 match = backend.dm.requests[backend.dm.requests['request_id'] == t_id]
                 if not match.empty:
                     r = match.iloc[0]
                     st.info(f"Status: {r['status']} | Date: {r['assigned_date']}")
                 else:
                     st.error("Not Found")
