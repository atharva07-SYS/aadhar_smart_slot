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

# --- CUSTOM CSS (V5 Design System: Inter, Spacing, Hierarchy) ---
st.markdown("""
    <style>
    /* VARIABLES */
    :root {
        --primary-red: #B72025; 
        --primary-yellow: #F3A12F;
        --primary-navy: #0B1E47;
        --bg-color: #F3F4F6; /* Cool Gray 50 */
        --text-header: #111827; /* Gray 900 */
        --text-body: #374151; /* Gray 700 */
        --text-sub: #6B7280; /* Gray 500 */
        --input-bg: #F9FAFB; /* Gray 50 */
        --border-color: #E5E7EB; /* Gray 200 */
    }

    /* GLOBAL TYPOGRAPHY ('INTER') */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-body);
        line-height: 1.6;
    }
    
    .stApp { background-color: var(--bg-color); }

    /* HEADERS */
    h1, h2, h3, h4 {
        color: var(--text-header);
        font-weight: 700;
        letter-spacing: -0.025em; /* Tight tracking for modern look */
        margin-bottom: 0.5em;
    }
    
    /* CARDS (Clean, Soft Shadow, High Spacing) */
    .gov-card {
        background: white;
        border-radius: 12px;
        padding: 40px; /* Breathe */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); /* Tailwind shadow-md */
        border: 1px solid var(--border-color);
        margin-bottom: 24px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .gov-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
    }
    
    /* GOV HEADER STRIP */
    .gov-strip {
        background: #F8F9FA;
        border-bottom: 1px solid #E5E7EB;
        padding: 8px 24px;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-sub);
        display: flex; justify-content: space-between; align-items: center;
    }
    .gov-strip strong { color: #111; }
    
    /* NAV HEADER */
    .brand-header {
        background: white;
        padding: 20px 32px;
        border-bottom: 1px solid #E5E7EB;
        display: flex; align-items: center; gap: 20px;
    }
    .brand-titles h1 { font-size: 1.5rem; margin:0; line-height:1.2; color: var(--primary-navy); }
    .brand-titles p { font-size: 0.875rem; margin:0; font-weight:500; color: var(--primary-red); text-transform:uppercase; letter-spacing:0.05em; }

    /* INPUTS (Height, Focus Ring) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        height: 50px !important; /* Taller */
        color: var(--text-header) !important;
        font-size: 1rem !important;
        padding-left: 16px !important;
        transition: all 0.2s;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: var(--primary-navy) !important;
        background-color: white !important;
        box-shadow: 0 0 0 3px rgba(11,30,71, 0.1) !important; /* Focus Ring */
    }

    /* BUTTONS */
    .stButton>button {
        background-color: var(--primary-navy);
        color: white;
        height: 50px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.95rem;
        border: none;
        padding: 0 32px;
        transition: all 0.2s;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stButton>button:hover {
        background-color: #1a3675; /* Lighter navy */
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] hr { margin: 24px 0; }
    
    /* ALERTS */
    .alert-box {
        padding: 16px; border-radius: 8px; font-weight: 500; font-size: 0.9rem;
        display: flex; align-items: center; margin-top: 20px;
    }
    .alert-success { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    
    </style>
""", unsafe_allow_html=True)

# --- ASSETS ---
AADHAAR_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/c/cf/Aadhaar_Logo.svg" 
GOV_INDIA_EMBLEM = "https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"

# --- TOP STRIP ---
st.markdown(f"""
    <div class='gov-strip'>
        <div><strong>GOVERNMENT OF INDIA</strong></div>
        <div>Skip to Main Content &nbsp;|&nbsp; <span style='cursor:pointer'>A+</span> <span style='cursor:pointer'>A-</span> &nbsp;|&nbsp; Language: <b>English</b></div>
    </div>
    <header class='brand-header'>
        <img src="{GOV_INDIA_EMBLEM}" style="height:56px; opacity:0.9;">
        <div style="width:1px; height:40px; background:#E5E7EB;"></div>
        <div class='brand-titles'>
             <h1>Unique Identification Authority of India</h1>
             <p>Government of India</p>
        </div>
        <div style="flex-grow:1"></div>
        <img src="{AADHAAR_LOGO_URL}" style="height:64px;">
    </header>
    <div style="height:4px; background:linear-gradient(90deg, #F3A12F 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);"></div>
    <br>
""", unsafe_allow_html=True)

# --- BACKEND ---
@st.cache_resource
def get_backend():
    return CrowdSystemBackend()

backend = get_backend()

# ================= AUTH STATE =================
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False
    st.session_state['admin_region'] = None

# ================= ADMIN CONSOLE (SIDEBAR) =================
if st.session_state['admin_logged_in']:
    region = st.session_state['admin_region']
    
    with st.sidebar:
        st.write("#### ASK Console")
        st.caption(f"Authenticated: {region}")
        st.markdown("---")
        nav = st.radio("Navigate", ["Overview", "Schedule System", "Analytics", "Emergency"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Sign Out"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

    # DATA SCOPING
    df = backend.dm.requests.copy().fillna('')
    scope_df = df[df['input_city'].str.contains(region, case=False)]

    if nav == "Overview":
        st.markdown(f"## Regional Dashboard: {region}")
        st.markdown("Real-time metrics from the Aadhaar Seva Kendra network.")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Requests", len(scope_df))
        c2.metric("Today's Slot", len(scope_df[scope_df['assigned_date'] == str(datetime.date.today())]))
        c3.metric("Pending", len(scope_df[scope_df['status'].str.contains("Confirmed")]))
        c4.metric("Operations", "Normal", delta="Online", delta_color="normal")
        
        st.write("")
        st.write("### Recent Activity")
        st.dataframe(scope_df.tail(10)[['request_id', 'name', 'phone', 'status']], use_container_width=True, hide_index=True)

    elif nav == "Analytics":
        st.subheader("Demographic Insights")
        c1, c2 = st.columns(2)
        with c1:
             st.markdown("<div class='gov-card'><h5>Age Breakdown</h5>", unsafe_allow_html=True)
             if not scope_df.empty:
                 fig = px.donut(scope_df, names='age_group', color_discrete_sequence=['#B72025', '#F3A12F', '#0B1E47'], hole=0.6)
                 fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
                 st.plotly_chart(fig, use_container_width=True)
             st.markdown("</div>", unsafe_allow_html=True)
        with c2:
             st.markdown("<div class='gov-card'><h5>Service Requests</h5>", unsafe_allow_html=True)
             if not scope_df.empty:
                fig2 = px.bar(scope_df, x='request_type', color='request_type', color_discrete_sequence=px.colors.qualitative.Prism)
                fig2.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig2, use_container_width=True)
             st.markdown("</div>", unsafe_allow_html=True)

    elif nav == "Emergency":
        col_em, _ = st.columns([1,1])
        with col_em:
            st.markdown("<div class='gov-card' style='border-left: 4px solid #EF4444;'>", unsafe_allow_html=True)
            st.write("#### ⚠️ Center Outage Simulation")
            st.write("Triggering an outage will auto-notify all scheduled appointments via SMS.")
            if st.button("INITIATE OUTAGE PROTOCOL"):
                with st.spinner("Broadcasting Emergency SMS..."):
                    time.sleep(2)
                st.error("Protocol Active: Users Notified.")
            st.markdown("</div>", unsafe_allow_html=True)

# ================= CITIZEN PORTAL =================
else:
    with st.sidebar:
        st.write("#### myAadhaar Login")
        role = st.selectbox("Select User Type", ["Resident", "Official / Admin"], label_visibility="collapsed")
        
        if role == "Official / Admin":
            st.info("Validation Required")
            with st.form("login"):
                uid = st.text_input("User ID", placeholder="admin_city_pincode")
                pwd = st.text_input("Password", type="password")
                if st.form_submit_button("Authenticate"):
                    if pwd == "admin123" and uid.startswith("admin_"):
                        parts = uid.split('_')
                        st.session_state['admin_logged_in'] = True
                        st.session_state['admin_region'] = parts[1].capitalize()
                        st.rerun()
                    else: st.error("Access Denied")
            st.caption("Try: admin_delhi_110001 / admin123")

    # HOME
    if role == "Resident":
        st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#0B1E47; margin-top:20px;'>Book an Appointment</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#6B7280; margin-bottom:40px;'>Secure your slot at an Aadhaar Seva Kendra close to you.</p>", unsafe_allow_html=True)

        st.markdown("<div class='gov-card'>", unsafe_allow_html=True)
        st.markdown("#### 📝 Resident Details")
        st.markdown("---")
        
        with st.form("book_slot"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name", placeholder="As per Proof of Identity")
                phone = st.text_input("Mobile Number", placeholder="10 Digit Number")
                city = st.selectbox("City / District", ["New Delhi", "Mumbai", "Bengaluru", "Noida", "Ghaziabad", "Gurugram"])
            with c2:
                age = st.number_input("Age", 0, 100, step=1)
                req = st.selectbox("Request Type", ["New Enrolment", "Biometric Update", "Demographic Update"])
                pin = st.text_input("Pincode", placeholder="Postal Code")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Check Availability & Book")

            if submitted:
                if not name or len(phone) != 10:
                    st.error("Please ensure all fields are filled correctly.")
                else:
                    with st.spinner("Verifying Availability..."):
                        time.sleep(1)
                        age_g = "Child (0-18)" if age < 18 else "Adult (18-60)" if age < 60 else "Senior (60+)"
                        payload = {"name": name, "phone": phone, "age": str(age), "age_group": age_g, "request_type": req, "user_type": "Scheduled", "city": city, "pincode": pin}
                        
                        res = backend.process_request(payload)
                        if res['success']:
                            d = res['data']
                            st.balloons()
                            st.markdown(f"""
                                <div class='alert-box alert-success'>
                                    <div>
                                        ✅ <b>Appointment Confirmed</b><br>
                                        Your Request ID is <b>{d['request_id']}</b>.<br>
                                        Scheduled at <b>{res['center_name']}</b> on {d['assigned_date']} ({d['assigned_time_slot']}).
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(res['message'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        # STATUS CHECK
        with st.expander("🔍 Retrieve Application Status"):
             sid = st.text_input("Enter Request ID (RID)")
             if st.button("Search"):
                 m = backend.dm.requests[backend.dm.requests['request_id'] == sid]
                 if not m.empty:
                     r = m.iloc[0]
                     st.info(f"Status: {r['status']}")
                 else: st.warning("No records found.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
    <div style='text-align:center; color:#9CA3AF; font-size:0.8rem; margin-top:60px; padding:40px; border-top:1px solid #E5E7EB;'>
        <p>Copyright © 2026 Unique Identification Authority of India. All rights reserved.</p>
        <p>
            <a href='#' style='color:#6B7280; text-decoration:none; margin:0 10px;'>Website Policy</a>
            <a href='#' style='color:#6B7280; text-decoration:none; margin:0 10px;'>Terms & Conditions</a>
            <a href='#' style='color:#6B7280; text-decoration:none; margin:0 10px;'>Privacy Policy</a>
        </p>
    </div>
""", unsafe_allow_html=True)
