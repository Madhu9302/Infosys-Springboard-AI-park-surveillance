# import streamlit as st
# import json
# import os
# from PIL import Image

# st.set_page_config(page_title="YOLO Streamlit", layout="wide")
# USER_DB = "users.json"
# MODEL_PATH = "yolo11s.pt"  # adjust if model is in another folder

# # ---------- user DB ----------
# def load_users():
#     if os.path.exists(USER_DB):
#         with open(USER_DB, "r") as f:
#             return json.load(f)
#     return {}

# def save_users(users):
#     with open(USER_DB, "w") as f:
#         json.dump(users, f, indent=4)

# # ---------- model loader (import inside) ----------
# @st.cache_resource
# def load_model(path=MODEL_PATH):
#     # Import here to avoid ultralytics running threads at module import time
#     try:
#         from ultralytics import YOLO
#     except Exception as e:
#         st.error(f"Cannot import ultralytics: {e}")
#         return None

#     try:
#         model = YOLO(path)
#         return model
#     except Exception as e:
#         st.error(f"Error loading model: {e}")
#         return None

# # ---------- auth ----------
# def register():
#     st.header("Register")
#     u = st.text_input("Username", key="r_user")
#     p = st.text_input("Password", type="password", key="r_pass")
#     if st.button("Create Account"):
#         users = load_users()
#         if not u:
#             st.error("Enter username")
#         elif u in users:
#             st.warning("User exists")
#         else:
#             users[u] = p  # production: hash password!
#             save_users(users)
#             st.success("Account created")

# def login():
#     st.header("Login")
#     u = st.text_input("Username", key="l_user")
#     p = st.text_input("Password", type="password", key="l_pass")
#     if st.button("Login"):
#         users = load_users()
#         if u in users and users[u] == p:
#             st.session_state["logged_in"] = True
#             st.session_state["username"] = u
#             st.success("Logged in")
#         else:
#             st.error("Invalid credentials")

# # ---------- dashboard ----------
# def run_dashboard():
#     st.title("YOLO Detection Dashboard")
#     st.write("User:", st.session_state.get("username", "Guest"))

#     model = load_model()
#     if model is None:
#         st.warning("Model not loaded. Check model path or ultralytics installation.")
#         return

#     uploaded = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])
#     if uploaded:
#         img = Image.open(uploaded).convert("RGB")
#         st.image(img, caption="Uploaded", use_column_width=True)

#         if st.button("Detect"):
#             # run detection (Ultralytics accepts PIL in newer versions)
#             results = model(img)
#             annotated = results[0].plot()  # may return numpy array or PIL

#             # Convert numpy->PIL if needed
#             try:
#                 import numpy as np
#                 if isinstance(annotated, np.ndarray):
#                     annotated = Image.fromarray(annotated[:, :, ::-1])  # BGR->RGB
#             except Exception:
#                 pass

#             st.image(annotated, caption="Result", use_column_width=True)
#             annotated.save("detection_out.jpg")
#             with open("detection_out.jpg", "rb") as f:
#                 st.download_button("Download", data=f, file_name="detection_out.jpg", mime="image/jpeg")

# # ---------- main ----------
# def main():
#     if "logged_in" not in st.session_state:
#         st.session_state["logged_in"] = False

#     choice = st.sidebar.selectbox("Menu", ["Login", "Register", "Dashboard"])
#     if choice == "Login":
#         login()
#     elif choice == "Register":
#         register()
#     elif choice == "Dashboard":
#         if st.session_state["logged_in"]:
#             run_dashboard()
#         else:
#             st.info("Please login first")

# if __name__ == "__main__":
#     main()
# app.py
# app.py
import streamlit as st
import json
import os
import hashlib
from datetime import datetime
from PIL import Image
from collections import Counter

# ---------- CONFIG ----------
st.set_page_config(page_title="YOLO Dashboard", layout="wide", page_icon="🚦", initial_sidebar_state="expanded")

# Paths (adjust if needed)
USER_DB = "users.json"
HISTORY_DB = "history.json"
MODEL_PATH = "yolo11s.pt"  # change if model is in another folder

# ---------- LIGHT CSS (modern look) ----------
st.markdown(
    """
    <style>
    /* Page */
    .reportview-container .main .block-container{
        padding-top: 1.2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* Header */
    .app-header {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .brand {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
    }
    .sub {
        color: #475569;
        font-size: 13px;
    }
    /* Card look */
    .card {
        border-radius: 12px;
        padding: 12px;
        background: white;
        box-shadow: 0 6px 18px rgba(15,23,42,0.06);
    }
    /* Hide Streamlit footer/menu for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HELPERS: file db ----------
def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------- PASSWORD (hash) ----------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# ---------- USER DB ----------
def load_users():
    return load_json(USER_DB)

def save_users(users):
    save_json(USER_DB, users)

# ---------- HISTORY DB ----------
def add_history(entry: dict):
    data = load_json(HISTORY_DB)
    if not isinstance(data, list):
        data = []
    data.insert(0, entry)  # newest first
    # keep last 50
    data = data[:50]
    save_json(HISTORY_DB, data)

def get_history():
    data = load_json(HISTORY_DB)
    if isinstance(data, list):
        return data
    return []

# ---------- MODEL LOADER (lazy inside function) ----------
@st.cache_resource
def load_model(path=MODEL_PATH):
    # Import here to avoid side-effects at module import time
    try:
        from ultralytics import YOLO
    except Exception as e:
        st.error(f"Failed to import ultralytics: {e}")
        return None

    if not os.path.exists(path):
        st.error(f"Model file not found at {path}. Update MODEL_PATH.")
        return None

    try:
        model = YOLO(path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# ---------- AUTH UI ----------
def register_ui():
    st.subheader("Create an account")
    col1, col2 = st.columns([2,1])
    with col1:
        username = st.text_input("Username", key="reg_user")
        email = st.text_input("Email (optional)", key="reg_email")
    with col2:
        password = st.text_input("Password", type="password", key="reg_pass")
    if st.button("Register", key="reg_btn"):
        if not username or not password:
            st.error("Username and password required")
            return
        users = load_users()
        if username in users:
            st.warning("Username already exists. Try login or choose different name.")
            return
        users[username] = {
            "password": hash_password(password),
            "email": email,
            "created_at": datetime.utcnow().isoformat()
        }
        save_users(users)
        st.success("Account created. Go to Login.")

def login_ui():
    st.subheader("Welcome back")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login", key="login_btn"):
        users = load_users()
        if username in users and users[username]["password"] == hash_password(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful! Redirecting to Dashboard...")
        else:
            st.error("Invalid credentials")

# ---------- DASHBOARD UI ----------
def dashboard_ui():
    st.markdown(
        """
        <div class="app-header">
            <div class="brand">🚦 YOLO Detection Studio</div>
            <div class="sub">Modern dashboard • Image upload • Detection history</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Top metrics
    history = get_history()
    total_images = len(history)
    total_users = len(load_users())

    # compute top classes from history
    all_classes = []
    for h in history:
        all_classes.extend(h.get("classes", []))
    top = Counter(all_classes).most_common(5)
    classes_dict = {k: v for k, v in top}

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Detections", total_images)
    m2.metric("Registered Users", total_users)
    m3.metric("Recent User", history[0]["user"] if history else "—")

    st.markdown("### Detection Workspace", unsafe_allow_html=True)

    left, right = st.columns([2,1])

    with left:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload an image to detect", type=["png","jpg","jpeg"])
            st.caption("Supported: JPG/PNG. Max file size depends on Streamlit config.")
            st.markdown("</div>", unsafe_allow_html=True)

            if uploaded:
                img = Image.open(uploaded).convert("RGB")
                st.image(img, caption="Uploaded image", use_column_width=True)

                # options
                conf = st.slider("Confidence threshold", 0.1, 0.9, 0.3, 0.05)
                show_labels = st.checkbox("Show labels on image", value=True)
                detect_btn = st.button("Run Detection")

                if detect_btn:
                    with st.spinner("Running YOLO..."):
                        model = load_model()
                        if model is None:
                            st.error("Model not available.")
                        else:
                            # run model on PIL image
                            results = model(img, conf=conf)
                            # annotated image
                            annotated = results[0].plot()
                            # convert numpy -> PIL if required
                            try:
                                import numpy as np
                                if isinstance(annotated, np.ndarray):
                                    annotated = Image.fromarray(annotated[:, :, ::-1])
                            except Exception:
                                pass

                            # show result
                            st.image(annotated, caption="Detection result", use_column_width=True)
                            # save result to file
                            out_path = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                            annotated.save(out_path)

                            # gather classes
                            detected_classes = []
                            try:
                                boxes = results[0].boxes
                                for b in boxes:
                                    # attempt to get class name if available
                                    cls = getattr(b, "cls", None)
                                    if cls is not None:
                                        # if class names available in model.names map
                                        try:
                                            name = results[0].names[int(cls)]
                                        except Exception:
                                            name = str(cls)
                                        detected_classes.append(name)
                            except Exception:
                                # fallback if structure different
                                pass

                            # save history entry
                            entry = {
                                "timestamp": datetime.utcnow().isoformat(),
                                "user": st.session_state.get("username", "guest"),
                                "image": uploaded.name,
                                "out_file": out_path,
                                "classes": detected_classes
                            }
                            add_history(entry)
                            st.success("Detection finished and saved to history.")
                            # download button
                            with open(out_path, "rb") as f:
                                st.download_button("Download Result", f, file_name=os.path.basename(out_path), mime="image/jpeg")

    with right:
        st.markdown("### Live Insights", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("Top detected classes (recent):")
        if classes_dict:
            st.bar_chart(classes_dict)
        else:
            st.info("No detections yet. Run detection to populate insights.")

        st.markdown("---")
        st.write("Recent History")
        hist = get_history()
        if hist:
            for h in hist[:6]:
                st.write(f"**{h['image']}** — {h['user']} — {h['timestamp'].split('T')[0]}")
                if h.get("classes"):
                    st.caption(", ".join(h["classes"]))
                st.markdown("---")
        else:
            st.info("History empty.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Manage Account")
    if st.button("Logout"):
        for k in list(st.session_state.keys()):
            st.session_state.pop(k)
        st.success("Logged out. Refresh the page.")

# ---------- ABOUT ----------
def about_ui():
    st.header("About YOLO Detection Studio")
    st.write("""
    - Built with Streamlit + Ultralytics YOLO  
    - Upload an image, detect objects, download annotated result  
    - Lightweight user system and detection history.
    """)
    st.write("Tip: Keep the model file (yolo11s.pt) in the same folder or update MODEL_PATH variable.")

# ---------- MAIN ----------
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # Sidebar navigation
    st.sidebar.markdown("## Navigation")
    nav = st.sidebar.radio("", ["Login", "Register", "Dashboard", "About"], index=2 if st.session_state["logged_in"] else 0)

    # show small account info in sidebar
    st.sidebar.markdown("---")
    if st.session_state["logged_in"]:
        st.sidebar.write(f"Signed in as **{st.session_state.get('username')}**")
        if st.sidebar.button("Logout (sidebar)"):
            for k in list(st.session_state.keys()):
                st.session_state.pop(k)
            st.experimental_rerun()
    else:
        st.sidebar.info("Please login or register to use the dashboard.")

    # Route
    if nav == "Login":
        login_ui()
    elif nav == "Register":
        register_ui()
    elif nav == "Dashboard":
        if st.session_state["logged_in"]:
            dashboard_ui()
        else:
            st.warning("Login required to access Dashboard.")
            login_ui()
    elif nav == "About":
        about_ui()

if __name__ == "__main__":
    main()
