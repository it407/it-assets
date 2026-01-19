import streamlit as st
import duckdb
import pandas as pd

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────
# Security & UI
# ─────────────────────────────
apply_global_ui()
admin_or_manager_only()
logout()

st.title("💻 Assigned Software")

# ─────────────────────────────
# Load data
# ─────────────────────────────
software_assign_df = read_sheet("software_assignments")
software_master_df = read_sheet("software_master")
employee_df = read_sheet("employee_master")

for df in [software_assign_df, software_master_df, employee_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# Guard
if software_assign_df.empty:
    st.info("No software assignments found.")
    st.stop()

# ─────────────────────────────
# DuckDB Join
# ─────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("software_assign", software_assign_df)
con.register("software_master", software_master_df)
con.register("employee", employee_df)

software_df = con.execute("""
SELECT
    e.employee_id,
    e.employee_name,
    sm.soft_id,
    sm.soft_name,
    sm.links AS link,
    e.department,
    e.location,
    s.assigned_on
FROM software_assign s
JOIN software_master sm ON s.soft_id = sm.soft_id
JOIN employee e ON s.employee_id = e.employee_id
WHERE s.assignment_status = 'Assigned'
""").df()

if software_df.empty:
    st.info("No assigned software found.")
    st.stop()

# ─────────────────────────────
# Filters
# ─────────────────────────────
st.subheader("🔍 Filters")

c1, c2, c3 = st.columns(3)

with c1:
    search = st.text_input("Search Employee (ID / Name)")

with c2:
    dept_filter = st.selectbox(
        "Department",
        ["All"] + sorted(software_df["department"].dropna().unique().tolist())
    )

with c3:
    location_filter = st.selectbox(
        "Location",
        ["All"] + sorted(software_df["location"].dropna().unique().tolist())
    )

if search:
    software_df = software_df[
        software_df["employee_id"].str.contains(search, case=False, na=False)
        | software_df["employee_name"].str.contains(search, case=False, na=False)
    ]

if dept_filter != "All":
    software_df = software_df[software_df["department"] == dept_filter]

if location_filter != "All":
    software_df = software_df[software_df["location"] == location_filter]

software_df = software_df.sort_values("assigned_on", ascending=False)

# ─────────────────────────────
# TABLE VIEW
# ─────────────────────────────
st.subheader("📋 Assigned Software")

display_cols = [
    "employee_id",
    "employee_name",
    "soft_id",
    "soft_name",
    "department",
    "location",
    "assigned_on",
    "link",
]

st.dataframe(
    software_df[display_cols],
    use_container_width=True,
    column_config={
        "link": st.column_config.LinkColumn(
            "Software Link",
            help="Open software portal",
            display_text="Open"
        )
    }
)

# ─────────────────────────────
# Export
# ─────────────────────────────
st.download_button(
    "⬇ Download CSV",
    data=software_df[display_cols].to_csv(index=False),
    file_name="assigned_software.csv",
    mime="text/csv",
)
