import streamlit as st
import cv2
import tempfile
import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from streamlit_app.auth import login_page, register_page
from streamlit_app.chatbot import park_chatbot
from inference.yolo_infer import run_inference
from logic.authorization import ActivityType

# Page Config
st.set_page_config(
    page_title="ParkGuard AI", 
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- PROFESSIONAL CSS ----------------
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hero Section */
    .hero-container {
        padding: 4rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
        border-radius: 0 0 50px 50px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Status Badges */
    .status-safe {
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #badbcc;
    }
    .status-danger {
        background-color: #f8d7da;
        color: #842029;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #f5c2c7;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Custom Buttons */
    .stButton>button {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "gemini_api_key" not in st.session_state:
    # Pre-fill with user provided key for convenience
    st.session_state.gemini_api_key = "AIzaSyA-KyRKljsaHo6slZa7-fEcYgJy9qZiKb8"

# Navigation Functions
def nav_to(page):
    st.session_state.page = page
    st.rerun()

# ---------------- VIEWS ----------------

def landing_page():
    # Hero
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🛡️ ParkGuard AI</div>
            <div class="hero-subtitle">Next-Generation Surveillance & Activity Analysis System</div>
        </div>
    """, unsafe_allow_html=True)

    # Call to Action
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Get Started / Login", use_container_width=True):
            nav_to("auth")

    st.markdown("---")

    # Features
    st.markdown("<h2 style='text-align: center;'>Why Choose ParkGuard?</h2><br>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">👁️</div>
                <h3>Real-Time Detection</h3>
                <p>Advanced YOLOv11 algorithms detect and classify activities instantly with high precision.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with f2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3>AI Security Assistant</h3>
                <p>Integrated OpenAI Chatbot that understands security contexts and answers queries.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with f3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3>Secure Logging</h3>
                <p>Complete dashboard with authorized/unauthorized classification and evidence logging.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # How It Works
    st.markdown("<h2 style='text-align: center;'>How It Works</h2><br>", unsafe_allow_html=True)
    
    st.markdown("""
    1.  **Login/Register**: Securely access the platform.
    2.  **Upload Media**: Drag & drop surveillance images or CCTV footage.
    3.  **Instant Analysis**: System flags unauthorized activities (Violence, Weapons) in Red.
    4.  **Consult AI**: Ask the chatbot for details or safety protocols.
    """)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<center style='color: #666;'>ParkGuard AI © 2026 | Enterprise Edition</center>", unsafe_allow_html=True)

def auth_view():
    st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <h1>🔐 Secure Access</h1>
        <p>Please log in to access the Security Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_page()
        with tab2:
            register_page()
            
    if st.button("← Back to Home"):
        nav_to("home")

def dashboard_view():
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1164/1164620.png", width=60) 
        st.header(f"Operator: {st.session_state.user}")
        st.caption("🟢 System Online")
        st.markdown("---")
        
        menu = st.radio("Navigation", ["Dashboard", "AI Chatbot", "Settings"])
        
        st.markdown("---")
        if st.button("Logout", type="primary"):
            st.session_state.logged_in = False
            nav_to("home")

    # Routing
    if menu == "Dashboard":
        render_dashboard()
    elif menu == "AI Chatbot":
        render_chatbot()
    elif menu == "Settings":
        render_settings()

def render_dashboard():
    st.title("📊 Security Ops Center")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Status", "Active", "OK")
    m2.metric("Network", "4 Cameras", "Connected")
    m3.metric("Uptime", "24h 12m", "+1h")
    m4.metric("Threat Level", "Low", "Stable")
    
    st.divider()

    col_upload, col_display = st.columns([1, 2])
    
    with col_upload:
        st.subheader("📡 Feed Input")
        tab_img, tab_vid = st.tabs(["Image", "Video"])
        
        source = None
        is_video = False
        
        with tab_img:
            img = st.file_uploader("Upload Frame", type=['jpg', 'png', 'jpeg'], key="img_upl")
            if img:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                tfile.write(img.read())
                source = tfile.name
        
        with tab_vid:
            vid = st.file_uploader("Upload Footage", type=['mp4', 'mov', 'avi'], key="vid_upl")
            if vid:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(vid.read())
                source = tfile.name
                is_video = True
                
    if source:
        with col_display:
            st.subheader("🔍 Analysis Result")
            if is_video:
                # Video Logic
                cap = cv2.VideoCapture(source)
                stframe = st.empty()
                stop_btn = st.button("Stop Stream", key="stop_vid")
                
                while cap.isOpened() and not stop_btn:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    p_frame, dets, summary = run_inference(frame, conf_threshold=st.session_state.get("conf_threshold", 0.45))
                    
                    if summary[ActivityType.UNAUTHORIZED] > 0:
                         cv2.putText(p_frame, "! ALERT !", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 3)
                    
                    stframe.image(p_frame, channels="RGB", use_container_width=True)
                cap.release()
            else:
                # Image Logic
                with st.spinner("Processing High-Res Frame..."):
                    p_img, dets, summary = run_inference(source, conf_threshold=st.session_state.get("conf_threshold", 0.45))
                
                st.image(p_img, use_container_width=True, caption="Analyzed Evidence")
                
                # Context for Chatbot
                st.session_state.last_detection_context = f"Found {len(dets)} objects. Authorized: {summary[ActivityType.AUTHORIZED]}, Unauthorized: {summary[ActivityType.UNAUTHORIZED]}."
                
                # Report
                st.markdown("### Threat Assessment")
                if summary[ActivityType.UNAUTHORIZED] > 0:
                    st.markdown(f'<div class="status-danger">⚠️ THREAT DETECTED ({summary[ActivityType.UNAUTHORIZED]})</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-safe">✅ AREA SECURE</div>', unsafe_allow_html=True)
                
                with st.expander("View Detailed Logs"):
                    st.json(dets)

def render_chatbot():
    context = st.session_state.get("last_detection_context", "No active analysis data.")
    park_chatbot(detection_context=context)

def render_settings():
    st.header("⚙️ System Configuration")
    st.info("System settings are stored locally in the session.")
    
    st.text_input("Gemini API Key (for Chatbot)", type="password", key="gemini_api_key")
    # if api_key: st.session_state.gemini_api_key = api_key # Handled automatically by key= argument
        
    st.markdown("### Detection Sensitivity")
    st.slider("Model Confidence Threshold", 0.0, 1.0, 0.45, key="conf_threshold")

# ---------------- MAIN ROUTER ----------------

if st.session_state.logged_in:
    dashboard_view()
else:
    if st.session_state.page == "home":
        landing_page()
    elif st.session_state.page == "auth":
        auth_view()
    else:
        landing_page() # Fallback
