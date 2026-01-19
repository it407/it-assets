import streamlit as st
import pandas as pd
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, append_row
from utils.ui import back_to_home_button
from utils.auth import logout

# ─────────────────────────────────────────────
# Security
# ─────────────────────────────────────────────
admin_only()
back_to_home_button()
logout()

st.title("📡 CCTV / Wi-Fi Credentials")

SHEET_NAME = "cctv_wifi_credential"

# ─────────────────────────────────────────────
# Load existing credentials
# ─────────────────────────────────────────────
cred_df = read_sheet(SHEET_NAME)
if not cred_df.empty:
    cred_df.columns = cred_df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# Submission form
# ─────────────────────────────────────────────
with st.form("cctv_wifi_form"):
    col1, col2 = st.columns(2)

    with col1:
        location = st.text_input("Location *")
        device_type = st.selectbox(
            "Device Type *",
            ["WiFi Router", "CCTV Camera", "NVR / DVR", "Switch", "Other"]
        )
        ssid = st.text_input("SSID / Device Name *")
        ssid_password = st.text_input("SSID / Device Password *")

    with col2:
        username = st.text_input("Username")
        password = st.text_input("Admin Password")
        ip_add = st.text_input("IP Address")
        mac = st.text_input("MAC Address")
        remarks = st.text_area("Remarks")

    submit = st.form_submit_button("➕ Save Credential")

# ─────────────────────────────────────────────
# Submit logic
# ─────────────────────────────────────────────
if submit:
    if not location or not device_type or not ssid or not ssid_password:
        st.error("Location, Device Type, SSID and SSID Password are required.")
        st.stop()

    append_row(
        SHEET_NAME,
        {
            "device_type": device_type,
            "username": username,
            "password": password,
            "ip_add": ip_add,
            "ssid": ssid,
            "ssid_password": ssid_password,
            "location": location,
            "mac": mac,
            "remarks": remarks,
            "created_at": datetime.now().isoformat(),
        }
    )

    st.success("CCTV / Wi-Fi credential saved successfully")
    st.rerun()

# ─────────────────────────────────────────────
# Table view + CSV
# ─────────────────────────────────────────────
st.divider()
st.subheader("📋 Stored CCTV / Wi-Fi Credentials")

if cred_df.empty:
    st.info("No credentials found.")
else:
    display_df = (
        cred_df.sort_values("created_at", ascending=False)
        if "created_at" in cred_df.columns
        else cred_df
    )

    st.dataframe(display_df, use_container_width=True)

    st.download_button(
        "⬇ Download CSV",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="cctv_wifi_credentials.csv",
        mime="text/csv"
    )
