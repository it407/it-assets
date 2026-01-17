# app.py

import streamlit as st
from utils.permissions import login_required
from utils.auth import logout
from utils.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_USER, ROLE_HR

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IT Asset & Subscription Manager",
    layout="wide",
    page_icon="logo.png"  # optional favicon
)

# ─────────────────────────────────────────────
# Global UI Cleanup (ONLY HERE)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>

    /* Remove extra top spacing */
    .block-container {
        padding-top: 1rem;
    }

    /* Hide top-right toolbar (GitHub, Fork, Deploy) */
    header [data-testid="stToolbar"] {
        display: none;
    }

    /* Hide bottom-right Share floating button */
    a[href*="share.streamlit"] {
        display: none !important;
    }
    [data-testid="stShareButton"] {
        display: none !important;
    }

    /* Hide footer */
    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────
login_required()
user = st.session_state["user"]
role = user["role"]

# ─────────────────────────────────────────────
# 🔁 EARLY ROLE REDIRECT (CRITICAL)
# ─────────────────────────────────────────────
if role == ROLE_HR and not st.session_state.get("_hr_redirect"):
    st.session_state["_hr_redirect"] = True
    st.switch_page("pages/11_Attendance_Dashboard.py")
    st.stop()

if role == ROLE_USER and not st.session_state.get("_user_redirect"):
    st.session_state["_user_redirect"] = True
    st.switch_page("pages/5_My_Assets.py")
    st.stop()

# ─────────────────────────────────────────────
# Sidebar (AFTER redirect)
# ─────────────────────────────────────────────
st.sidebar.success(f"Logged in as {user['email']} ({role})")
logout()

# ─────────────────────────────────────────────
# Hide sidebar navigation (Manager & User)
# ─────────────────────────────────────────────
if role in [ROLE_MANAGER, ROLE_USER]:
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Dashboard Hub (Admin & Manager)
# ─────────────────────────────────────────────
st.title("📊 Dashboards")
st.markdown("Select a dashboard to continue:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Asset Dashboards")

    if st.button("📊 Asset Summary Dashboard"):
        st.switch_page("pages/1_Dashboard.py")

    if st.button("👥 User-wise Assigned Assets"):
        st.switch_page("pages/9_User_Asset_Assignments.py")

with col2:
    st.subheader("🔐 System")

    if role == ROLE_ADMIN:
        if st.button("🧭 Role Navigation Admin"):
            st.switch_page("pages/10_Role_Navigation_Admin.py")
