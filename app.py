import streamlit as st
import time
from start_attendance import start_attendance
from dataset import create_dataset
from encode_faces import encode_faces

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Attendance System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= STAFF CREDENTIALS =================
STAFF_ID = "admin"
STAFF_PASSWORD = "1234"

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.block-container { padding-top: 0rem !important; }
header, footer { visibility: hidden; }

/* animated background */
.stApp {
    min-height: 100vh;
    background: linear-gradient(120deg,#e0f2fe,#bae6fd,#7dd3fc,#38bdf8);
    background-size: 300% 300%;
    animation: bgFlow 6s ease-in-out infinite;
}
@keyframes bgFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* cards - FINAL BALANCED */
.card {
    background: rgba(255,255,255,0.65);
    border-radius: 24px;
    padding: 30px;
    backdrop-filter: blur(14px);
    box-shadow: 0 20px 45px rgba(2,132,199,0.35);

    margin-top: 20px;
}


/* buttons */
.stButton>button {
    width: 100%;
    padding: 13px;
    border-radius: 30px;
    font-size: 16px;
    font-weight: 700;
    background: linear-gradient(135deg,#0284c7,#38bdf8);
    color: white;
    border: none;
    box-shadow: 0 12px 28px rgba(14,165,233,0.6);
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE =================
def login_page():
    st.markdown("""
    <style>
    .login-box {
        background: rgba(255,255,255,0.7);
        padding: 38px;
        border-radius: 28px;
        backdrop-filter: blur(16px);
        box-shadow: 0 30px 70px rgba(2,132,199,0.5);
        animation: fadeUp 0.8s ease;
    }
    @keyframes fadeUp {
        from { transform: translateY(40px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .login-title {
        text-align: center;
        font-size: 30px;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .login-sub {
        text-align: center;
        font-size: 14px;
        color: #075985;
        margin-bottom: 26px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<div class='login-title'>🔐 Staff Login</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Authorized Access Only</div>", unsafe_allow_html=True)

        staff_id = st.text_input("Staff ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if staff_id == STAFF_ID and password == STAFF_PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("Invalid Staff ID or Password")

        st.markdown("</div>", unsafe_allow_html=True)

# ================= DASHBOARD =================
def dashboard():
    MONTHLY_SHEET_URL = "https://docs.google.com/spreadsheets/d/1H9a5JAMqG-lvBXQyxnda84VffAoNKHmyov4aMx1hYXY/edit"

    # monthly report button
    st.markdown(f"""
    <div style="position:fixed;top:16px;right:16px;z-index:9999;">
        <a href="{MONTHLY_SHEET_URL}" target="_blank">
            <button style="
                padding:10px 22px;
                border-radius:30px;
                background:linear-gradient(135deg,#0284c7,#38bdf8);
                color:white;
                font-weight:700;
                border:none;">
                📊 Monthly Report
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("<h1 style='text-align:center;'>AI Face Recognition Attendance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#075985;'>Smart • Automated • Secure Attendance System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # ===== DATASET =====
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📸 Dataset Collection")

        name = st.text_input("Student Name")
        reg_no = st.text_input("Register Number")

        if st.button("➕ Capture Dataset"):
            if name and reg_no:
                progress = st.progress(0)
                status = st.empty()

                status.markdown("📷 Opening Camera...")
                time.sleep(0.5); progress.progress(30)

                status.markdown("🙂 Capturing Images...")
                create_dataset(name, reg_no)
                progress.progress(90)

                status.success("✅ Dataset Created Successfully")
                progress.progress(100)
            else:
                st.warning("⚠ Enter Name & Register Number")

        st.markdown("</div>", unsafe_allow_html=True)

    # ===== ENCODING =====
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🧠 Face Encoding")

        if st.button("⚙ Generate Encodings"):
            progress = st.progress(0)
            status = st.empty()

            status.markdown("🔍 Reading Dataset...")
            time.sleep(0.6); progress.progress(40)

            status.markdown("🧠 Generating Encodings...")
            encode_faces()
            progress.progress(100)

            status.success("✅ Encoding Completed")

        st.markdown("</div>", unsafe_allow_html=True)

    # ===== ATTENDANCE =====
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🎥 Live Attendance")

        if st.button("▶ Start Attendance"):
            with st.spinner("🎥 Camera Starting..."):
                results = start_attendance()

            if results:
                for n, s in results:
                    st.write(f"✅ {n} → {s}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center;margin-top:40px;'>© 2026 | Final Year AI Project</p>", unsafe_allow_html=True)

# ================= ROUTER =================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()