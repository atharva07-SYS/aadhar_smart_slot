import streamlit as st
import pandas as pd
import time
import datetime
import plotly.express as px
from src.backend import CrowdSystemBackend

# --- CONFIG ---
st.set_page_config(
    page_title="myAadhaar | Government of India",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Official Premium Gov Theme) ---
st.markdown("""
    <style>
    /* VARIABLES */
    :root {
        --primary-red: #B72025; /* Official Aadhaar Red */
        --primary-yellow: #F3A12F; /* Official Aadhaar Yellow */
        --primary-navy: #0B1E47; /* Official Navy */
        --bg-color: #F8F9FA;
        --card-bg: #FFFFFF;
        --text-color: #333333;
    }

    /* GLOBAL */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Hind:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Hind', sans-serif;
    }

    /* GOV TOP STRIP */
    .gov-strip {
        background-color: #f1f1f1;
        color: #666;
        padding: 5px 20px;
        font-size: 0.8rem;
        border-bottom: 1px solid #ddd;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .gov-strip strong { color: #000; font-weight: 700; }

    /* HEADER */
    .brand-header {
        background: white;
        padding: 15px 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-bottom: 4px solid var(--primary-yellow);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .brand-logo { height: 60px; }
    .brand-title { 
        color: var(--primary-navy); 
        font-size: 1.8rem; 
        font-weight: 700; 
        line-height: 1.2;
    }
    .brand-subtitle {
        color: var(--primary-red);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* CARDS (Material minimal) */
    .gov-card {
        background: white;
        border-radius: 8px;
        padding: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #eee;
        margin-bottom: 20px;
        transition: box-shadow 0.2s;
    }
    .gov-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    /* BUTTONS */
    .stButton>button {
        background-color: var(--primary-navy);
        color: white;
        border-radius: 4px;
        height: 45px;
        padding: 0 25px;
        font-weight: 500;
        text-transform: uppercase;
        border: none;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: var(--primary-red);
        color: white;
    }
    .secondary-btn>button {
        background-color: white;
        color: var(--primary-navy);
        border: 2px solid var(--primary-navy);
    }

    /* INPUTS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        border-radius: 4px !important;
        border: 1px solid #ccc !important;
        background-color: #fff !important;
        color: #333 !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: var(--primary-navy) !important;
        box-shadow: 0 0 0 2px rgba(11,30,71,0.1);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #eee;
    }
    
    /* FOOTER */
    .gov-footer {
        background-color: var(--primary-navy);
        color: white;
        padding: 40px 20px;
        margin-top: 50px;
        font-size: 0.9rem;
        text-align: center;
    }
    .gov-footer a { color: #ccc; text-decoration: none; margin: 0 10px; }
    
    /* STATUS BADGES */
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .badge-success { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    .badge-warning { background: #fff3e0; color: #ef6c00; border: 1px solid #ffe0b2; }

    </style>
""", unsafe_allow_html=True)

# --- ASSETS ---
AADHAAR_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/c/cf/Aadhaar_Logo.svg" 
GOV_INDIA_EMBLEM = "https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"

# --- LAYOUT HEADER ---
st.markdown(f"""
    <div class='gov-strip'>
        <div><strong>GOVERNMENT OF INDIA</strong></div>
        <div>Skip to Main Content | <span style='font-size:1.1em'>A+ A-</span> | Language: <b style='color:#333'>English</b></div>
    </div>
    <div class='brand-header'>
        <img src="{GOV_INDIA_EMBLEM}" style="height:55px; opacity:0.8;">
        <div style="flex-grow:1; border-left:1px solid #ccc; padding-left:15px; margin-left:5px;">
             <div class='brand-title'>Unique Identification Authority of India</div>
             <div class='brand-subtitle'>Government of India</div>
        </div>
        <img src="{AADHAAR_LOGO_URL}" class='brand-logo'>
    </div>
    <div style="height:3px; background:linear-gradient(90deg, #F3A12F 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);"></div>
    <br>
""", unsafe_allow_html=True)

# --- BACKEND ---
@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# ================= STATE MANAGEMENT =================
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
    st.session_state['admin_region'] = None

# ================= ADMIN SIDEBAR CONTROLLER =================
if st.session_state['admin_logged_in']:
    region = st.session_state['admin_region']
    with st.sidebar:
        st.image(AADHAAR_LOGO_URL, width=150)
        st.write("### ASK Console")
        st.info(f"📍 **{region}**")
        nav = st.radio("Menu", ["Dashboard", "Schedule", "Analytics", "Alerts"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Secure Logout"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

    # --- ADMIN CONTENT ---
    df = backend.dm.requests.copy().fillna('')
    # Simulate strict scope
    scope_df = df[df['input_city'].str.contains(region, case=False)]

    if nav == "Dashboard":
        st.subheader("Regional Overview")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Applications", len(scope_df))
        today = len(scope_df[scope_df['assigned_date'] == str(datetime.date.today())])
        m2.metric("Today's Appointments", today)
        pending = len(scope_df[scope_df['status'].str.contains("Confirmed")])
        m3.metric("Pending Processing", pending)
        m4.metric("Center Status", "🟢 Online")
        
        st.write("")
        st.write("##### 📋 Recent Applications")
        st.dataframe(scope_df[['request_id', 'name', 'request_type', 'assigned_date', 'status']].tail(8), use_container_width=True, hide_index=True)

    elif nav == "Analytics":
        st.subheader("Demographics Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='gov-card'><b>Age Group Distribution</b>", unsafe_allow_html=True)
            if not scope_df.empty:
                fig = px.pie(scope_df, names='age_group', color_discrete_sequence=['#B72025', '#F3A12F', '#0B1E47'])
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='gov-card'><b>Service Requests</b>", unsafe_allow_html=True)
            if not scope_df.empty:
                fig2 = px.bar(scope_df, x='request_type', color='request_type', color_discrete_sequence=px.colors.qualitative.Prism)
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif nav == "Alerts":
        st.subheader("Network & Alerts")
        st.error("⚠️ EMERGENCY BROADCAST SYSTEM")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='gov-card'>", unsafe_allow_html=True)
            st.write("<b>Report Failure</b>")
            if st.button("TRIGGER OUTAGE ALERT"):
                with st.spinner("Notifying Central Command..."):
                    time.sleep(2)
                st.toast("🚨 ALERT SENT: Regional Outage Reported.")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='gov-card'>", unsafe_allow_html=True)
            st.write("<b>Mass Notification</b>")
            msg = st.text_input("SMS Content")
            if st.button("Send Blast"):
                st.success(f"Sent: {msg}")
            st.markdown("</div>", unsafe_allow_html=True)
            
    elif nav == "Schedule":
        st.subheader("Daily Manifest")
        d = st.date_input("Select Date", datetime.date.today())
        v_df = scope_df[scope_df['assigned_date'] == str(d)]
        if v_df.empty: st.info("No appointments.")
        else: st.dataframe(v_df, use_container_width=True)


# ================= CITIZEN VIEW =================
else:
    # Sidebar for Login Toggle
    with st.sidebar:
        st.image(AADHAAR_LOGO_URL, width=120)
        st.write("### myAadhaar")
        st.markdown("---")
        role = st.selectbox("Role", ["Citizen", "Official Login"])
        
        if role == "Official Login":
            with st.form("login_form"):
                uid = st.text_input("Official ID")
                pwd = st.text_input("Password", type="password")
                if st.form_submit_button("LOGIN"):
                    if pwd == "admin123" and uid.startswith("admin_"):
                        parts = uid.split('_')
                        st.session_state['admin_logged_in'] = True
                        st.session_state['admin_region'] = parts[1].capitalize()
                        st.rerun()
                    else: st.error("Access Denied")
            st.caption("Demo: admin_delhi_110001 / admin123")

    # MAIN CONTENT
    if role == "Citizen":
        st.markdown("<h2 style='text-align:center; color:#0B1E47'>Book Appointment</h2><br>", unsafe_allow_html=True)
        
        c_main, _ = st.columns([1, 0.05])
        
        st.markdown("<div class='gov-card'>", unsafe_allow_html=True)
        st.write("#### 📝 Enrolment / Update Form")
        st.markdown("---")
        
        with st.form("book_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", help="Name as per supporting documents (POI)")
                phone = st.text_input("Mobile No.", help="10-digit indian mobile number")
                city = st.selectbox("Preferred City", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])
            
            with c2:
                age = st.number_input("Age (Years)", 0, 120)
                service = st.selectbox("Service Required", ["New Enrolment", "Biometric Update", "Demographic Update", "eKYC"])
                pincode = st.text_input("Area Pincode")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_c1, btn_c2 = st.columns([1, 2])
            with btn_c2:
                sub = st.form_submit_button("Search & Book Slot")
                
            if sub:
                if not name or len(phone) != 10:
                    st.error("Please enter valid mandatory details.")
                else:
                    with st.spinner("Validating Request..."):
                        time.sleep(1)
                        age_grp = "Child (0-18)" if age < 18 else "Adult (18-60)" if age < 60 else "Senior (60+)"
                        payload = {"name": name, "phone": phone, "age": str(age), "age_group": age_grp, "request_type": service, "user_type": "Scheduled", "city": city, "pincode": pincode}
                        
                        res = backend.process_request(payload)
                        if res['success']:
                            d = res['data']
                            st.success("✅ Appointment Successfully Booked")
                            st.markdown(f"""
                                <div style='background:#f9f9f9; padding:15px; border-left:4px solid #F3A12F; margin-top:20px;'>
                                    <div style='font-size:1.2rem; font-weight:bold; color:#0B1E47'>Request ID: {d['request_id']}</div>
                                    <div>Center: {res['center_name']}</div>
                                    <div>Slot: {d['assigned_date']} at {d['assigned_time_slot']}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(res['message'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("🔍 Check Application Status"):
            ck_id = st.text_input("Enter Enrolment ID (EID) or Request ID")
            if st.button("Check Status"):
                match = backend.dm.requests[backend.dm.requests['request_id'] == ck_id]
                if not match.empty:
                    r = match.iloc[0]
                    st.success(f"Current Status: {r['status']}")
                else: st.warning("Record Not Found")

# --- FOOTER ---
st.markdown("""
    <div class='gov-footer'>
        <div>
            <a href='#'>Website Policy</a> | 
            <a href='#'>Terms & Conditions</a> | 
            <a href='#'>Privacy Policy</a> | 
            <a href='#'>Hyperlink Policy</a> | 
            <a href='#'>Copyright Policy</a> | 
            <a href='#'>Help</a>
        </div>
        <br>
        <div>Content owned by Unique Identification Authority of India</div>
        <div>© 2026 Government of India</div>
    </div>
""", unsafe_allow_html=True)
