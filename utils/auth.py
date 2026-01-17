# utils/auth.py

import streamlit as st
from utils.gsheets import read_sheet
from utils.constants import USERS_SHEET

def login():
    if "user" in st.session_state:
        return

    st.title("🔐 IT Asset Management Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = read_sheet(USERS_SHEET)

        if users.empty:
            st.error("User access table is empty")
            st.stop()

        user = users[
            (users["email"] == email)
            & (users["password"] == password)
            & (users["is_active"].astype(str).str.lower() == "true")
        ]

        if user.empty:
            st.error("Invalid credentials or inactive user")
            st.stop()

        st.session_state["user"] = {
            "user_id": user.iloc[0]["user_id"],
            "employee_id": user.iloc[0]["employee_id"],
            "email": user.iloc[0]["email"],
            "role": user.iloc[0]["role"]
        }
        st.rerun()

def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
