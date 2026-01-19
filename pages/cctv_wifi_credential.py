import streamlit as st
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, append_row
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Security + UI
# ─────────────────────────────────────────────
apply_global_ui()
admin_only()
logout()

st.title("CCTV / Wi-Fi Credential")

SHEET_NAME = "cctv_wifi_credential"

# ─────────────────────────────────────────────
# Load existing data
# ─────────────────────────────────────────────
cred_df = read_sheet(SHEET_NAME)
if not cred_df.empty:
    cred_df.columns = cred_df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# Build dropdown options from table
# ─────────────────────────────────────────────
location_values = []
device_type_values = []

if not cred_df.empty:
    if "location" in cred_df.columns:
        location_values = sorted(
            set(
                cred_df["location"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )
        )

    if "device_type" in cred_df.columns:
        device_type_values = sorted(
            set(
                cred_df["device_type"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )
        )

# Fallback for first run
if not location_values:
    location_values = ["HO", "Branch 1", "Branch 2", "Warehouse"]

if not device_type_values:
    device_type_values = ["WiFi Router", "CCTV Camera", "NVR / DVR", "Switch"]

# Always add trigger option
location_options = location_values + ["Other"]
device_type_options = device_type_values + ["Other"]

# ─────────────────────────────────────────────
# Dynamic selectors (OUTSIDE FORM — IMPORTANT)
# ─────────────────────────────────────────────
st.subheader("📍 Device Location & Type")

location_choice = st.selectbox("Location *", location_options)

custom_location = ""
if location_choice == "Other":
    custom_location = st.text_input("Enter Location *")

device_type_choice = st.selectbox("Device Type *", device_type_options)

custom_device_type = ""
if device_type_choice == "Other":
    custom_device_type = st.text_input("Enter Device Type *")

# ─────────────────────────────────────────────
# Submission form (STATIC INPUTS ONLY)
# ─────────────────────────────────────────────
with st.form("cctv_wifi_form"):
    col1, col2 = st.columns(2)

    with col1:
        ssid = st.text_input("SSID / Device Name")
        ss_password = st.text_input("SSID Password")
        username = st.text_input("Username")
        password = st.text_input("Admin Password")

    with col2:
        ip_add = st.text_input("IP Address")
        mac = st.text_input("MAC Address")
        remarks = st.text_area("Remarks")

    submit = st.form_submit_button("➕ Save Credential")

# ─────────────────────────────────────────────
# Submit logic (RESOLVE FINAL VALUES)
# ─────────────────────────────────────────────
if submit:
    final_location = (
        custom_location.strip()
        if location_choice == "Other"
        else location_choice
    )

    final_device_type = (
        custom_device_type.strip()
        if device_type_choice == "Other"
        else device_type_choice
    )

    if not final_location or not final_device_type:
        st.error("Location and Device Type are required.")
        st.stop()

    append_row(
        SHEET_NAME,
        {
            "location": final_location,
            "device_type": final_device_type,
            "username": username,
            "password": password,
            "ip_add": ip_add,
            "ssid": ssid,
            "ss_password": ss_password,
            "mac": mac,
            "remarks": remarks,
            "created_at": datetime.now().isoformat(),
        }
    )

    st.success("CCTV / Wi-Fi credential saved successfully")
    st.rerun()

# ─────────────────────────────────────────────
# Table + CSV export
# ─────────────────────────────────────────────
st.divider()
st.subheader("📋 Stored CCTV / Wi-Fi Credentials")

cred_df = read_sheet(SHEET_NAME)
if not cred_df.empty:
    cred_df.columns = cred_df.columns.str.strip().str.lower()

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
