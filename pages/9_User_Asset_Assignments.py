import streamlit as st
import duckdb

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.export import export_csv
from utils.ui import apply_global_ui
from utils.auth import logout
from utils.constants import ASSET_ASSIGNMENTS_SHEET, ASSETS_MASTER_SHEET

# ─────────────────────────────────────────────
# Global UI + Security
# ─────────────────────────────────────────────
apply_global_ui()
admin_or_manager_only()
logout()

# ─────────────────────────────────────────────
# Back to Dashboard Hub
# ─────────────────────────────────────────────
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.title("👥 User Asset Assignments")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assignments_df = read_sheet(ASSET_ASSIGNMENTS_SHEET)
assets_df = read_sheet(ASSETS_MASTER_SHEET)
employees_df = read_sheet("employee_master")

if assignments_df.empty or assets_df.empty or employees_df.empty:
    st.warning("Required data is missing.")
    st.stop()

# Normalize columns
for df in [assignments_df, assets_df, employees_df]:
    df.columns = df.columns.str.strip().str.lower()

# Active assignments only
assigned_df = assignments_df[
    assignments_df["assignment_status"] == "Assigned"
]

if assigned_df.empty:
    st.info("No active asset assignments.")
    st.stop()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔎 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search_text = st.text_input(
        "Search Employee (ID or Name)",
        placeholder="EMP-001 or Nitesh"
    ).strip()

with col2:
    dept_options = ["All"] + sorted(
        employees_df["department"].dropna().unique().tolist()
    )
    department = st.selectbox("Department", dept_options)

with col3:
    loc_options = ["All"] + sorted(
        employees_df["location"].dropna().unique().tolist()
    )
    location = st.selectbox("Location", loc_options)

# ─────────────────────────────────────────────
# DuckDB Query (CORRECT PARAM HANDLING)
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("assignments", assigned_df)
con.register("assets", assets_df)
con.register("employees", employees_df)

query = """
SELECT
    a.assignment_id,
    a.asset_id,
    am.asset_name,
    am.category,
    a.employee_id,
    a.employee_name,
    e.department,
    e.location,
    a.assigned_on
FROM assignments a
LEFT JOIN assets am ON a.asset_id = am.asset_id
LEFT JOIN employees e ON a.employee_id = e.employee_id
WHERE 1=1
"""

params = []

if search_text:
    query += """
    AND (
        LOWER(a.employee_id) LIKE LOWER(?)
        OR LOWER(a.employee_name) LIKE LOWER(?)
    )
    """
    params.extend([f"%{search_text}%", f"%{search_text}%"])

if department != "All":
    query += " AND e.department = ?"
    params.append(department)

if location != "All":
    query += " AND e.location = ?"
    params.append(location)

query += " ORDER BY a.assigned_on DESC"

result_df = con.execute(query, params).df()

# ─────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────
st.subheader("📋 Assigned Assets (Current)")

if result_df.empty:
    st.info("No records found for selected filters.")
else:
    st.dataframe(result_df, use_container_width=True)
    export_csv(result_df, "user_wise_assigned_assets.csv")
