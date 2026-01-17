# utils/permissions.py

import streamlit as st
from utils.auth import login
from utils.constants import ROLE_ADMIN
from utils.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_HR
import streamlit as st

def login_required():
    if "user" not in st.session_state:
        login()
        st.stop()

def admin_only():
    login_required()
    if st.session_state["user"]["role"] != ROLE_ADMIN:
        st.error("Admin access required")
        st.stop()

def admin_or_manager_only():
    login_required()
    if st.session_state["user"]["role"] not in [ROLE_ADMIN, ROLE_MANAGER]:
        st.error("Access restricted")
        st.stop()

def hr_only():
    login_required()
    if st.session_state["user"]["role"] != ROLE_HR:
        st.error("HR access required")
        st.stop()