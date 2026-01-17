import streamlit as st
import pandas as pd

from utils.permissions import hr_only
from utils.auth import logout
from utils.ui import apply_global_ui
from utils.navigation import apply_role_based_navigation
apply_global_ui()
# ─────────────────────────────────────────────
# Global UI + Security
# ─────────────────────────────────────────────
hr_only()
apply_role_based_navigation()
logout()

st.title("📊 Attendance Dashboard")

# ─────────────────────────────────────────────
# Custom CSS (attendance specific)
# ─────────────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}
header [data-testid="stToolbar"] {
    display: none;
}
a[href*="share.streamlit"],
[data-testid="stShareButton"] {
    display: none !important;
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PUBLIC GOOGLE SHEET (CSV)
# ─────────────────────────────────────────────
SHEET_ID = "1FVjiK9Y-AhrogECD6Q8tRZpPiSxOFMevlMKGQWTGsHI"
SHEET_NAME = "odata"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(CSV_URL)
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["work_hours"] = pd.to_numeric(df["work_hours"], errors="coerce")
    return df

df = load_data()

if df.empty:
    st.warning("No data found in attendance sheet.")
    st.stop()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
with st.expander("🔍 Filters", expanded=True):
    search = st.text_input("Search (Emp ID / First Name)")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", df["log_date"].min().date())
    with col2:
        end_date = st.date_input("End Date", df["log_date"].max().date())

    col3, col4 = st.columns(2)
    with col3:
        day_status_filter = st.multiselect(
            "Day Status",
            sorted(df["day_status"].dropna().unique()),
            default=sorted(df["day_status"].dropna().unique())
        )
    with col4:
        leave_status_filter = st.multiselect(
            "Leave Status",
            sorted(df["leave_status"].dropna().unique()),
            default=sorted(df["leave_status"].dropna().unique())
        )

    user_type_filter = st.multiselect(
        "User Type",
        sorted(df["user_type"].dropna().unique()),
        default=sorted(df["user_type"].dropna().unique())
    )

# ─────────────────────────────────────────────
# Apply Filters
# ─────────────────────────────────────────────
filtered = df.copy()

if search:
    filtered = filtered[
        filtered["employee_fname"].str.contains(search, case=False, na=False)
        | filtered["empid"].astype(str).str.contains(search)
    ]

start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

filtered = filtered[
    (filtered["log_date"] >= start_dt)
    & (filtered["log_date"] <= end_dt)
    & (filtered["day_status"].isin(day_status_filter))
    & (filtered["leave_status"].isin(leave_status_filter))
    & (filtered["user_type"].isin(user_type_filter))
]

# ─────────────────────────────────────────────
# Work Hour Status
# ─────────────────────────────────────────────
def work_hour_status(hours):
    if pd.isna(hours):
        return "⚪ NA"
    if hours >= 8:
        return "🟢 Full"
    if hours >= 4:
        return "🟡 Partial"
    return "🔴 Low"

filtered["Work Hours Status"] = filtered["work_hours"].apply(work_hour_status)

# Display formatting
filtered["log_date"] = filtered["log_date"].dt.strftime("%Y-%m-%d")

display_cols = [
    "empid",
    "employee_fname",
    "employee_lname",
    "gender",
    "log_date",
    "user_type",
    "first_in_time",
    "last_out_time",
    "work_hours",
    "Work Hours Status",
    "day_status",
    "total_in_out",
    "leave_status"
]
display_cols = [c for c in display_cols if c in filtered.columns]

st.subheader("📋 Attendance Records")
st.dataframe(filtered[display_cols], use_container_width=True, height=520)

st.download_button(
    "⬇ Download Filtered CSV",
    data=filtered[display_cols].to_csv(index=False),
    file_name="attendance_filtered.csv",
    mime="text/csv"
)