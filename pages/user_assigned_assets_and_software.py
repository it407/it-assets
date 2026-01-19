import streamlit as st
import duckdb
import pandas as pd

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Security & UI
# ─────────────────────────────────────────────
apply_global_ui()
admin_or_manager_only()
logout()

st.title("👤 User-wise Assigned Assets & Software")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
asset_assign_df = read_sheet("asset_assignments")
asset_master_df = read_sheet("assets_master")
software_assign_df = read_sheet("software_assignments")
software_master_df = read_sheet("software_master")
employee_df = read_sheet("employee_master")

dfs = [
    asset_assign_df,
    asset_master_df,
    software_assign_df,
    software_master_df,
    employee_df,
]

for df in dfs:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# Guard
if asset_assign_df.empty and software_assign_df.empty:
    st.info("No assigned assets or software found.")
    st.stop()

# ─────────────────────────────────────────────
# DuckDB joins
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("asset_assign", asset_assign_df)
con.register("asset_master", asset_master_df)
con.register("software_assign", software_assign_df)
con.register("software_master", software_master_df)
con.register("employee", employee_df)

# ─────────────────────────────────────────────
# Assets query
# ─────────────────────────────────────────────
asset_df = con.execute("""
SELECT
    e.employee_id,
    e.employee_name,
    am.asset_id,
    am.asset_name,
    am.category,
    am.location,
    e.department,
    a.assigned_on
FROM asset_assign a
JOIN asset_master am ON a.asset_id = am.asset_id
JOIN employee e ON a.employee_id = e.employee_id
WHERE a.assignment_status = 'Assigned'
""").df()

# ─────────────────────────────────────────────
# Software query
# ─────────────────────────────────────────────
software_df = con.execute("""
SELECT
    e.employee_id,
    e.employee_name,
    sm.soft_id,
    sm.soft_name,
    sm.links,
    e.location,
    e.department,
    s.assigned_on
FROM software_assign s
JOIN software_master sm ON s.soft_id = sm.soft_id
JOIN employee e ON s.employee_id = e.employee_id
WHERE s.assignment_status = 'Assigned'
""").df()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔍 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("Search Employee (ID / Name)")

with col2:
    dept_filter = st.selectbox(
        "Department",
        ["All"] + sorted(
            pd.concat(
                [asset_df["department"], software_df["department"]],
                ignore_index=True
            ).dropna().unique().tolist()
        )
    )

with col3:
    location_filter = st.selectbox(
        "Location",
        ["All"] + sorted(
            pd.concat(
                [asset_df["location"], software_df["location"]],
                ignore_index=True
            ).dropna().unique().tolist()
        )
    )

def apply_filters(df):
    if search:
        df = df[
            df["employee_id"].str.contains(search, case=False, na=False)
            | df["employee_name"].str.contains(search, case=False, na=False)
        ]
    if dept_filter != "All":
        df = df[df["department"] == dept_filter]
    if location_filter != "All":
        df = df[df["location"] == location_filter]
    return df

asset_df = apply_filters(asset_df)
software_df = apply_filters(software_df)

# ─────────────────────────────────────────────
# Assigned Assets (DATAFRAME)
# ─────────────────────────────────────────────
st.divider()
st.subheader("🖥️ Assigned Assets")

if asset_df.empty:
    st.info("No assigned assets found.")
else:
    st.dataframe(
        asset_df[
            [
                "employee_id",
                "employee_name",
                "asset_id",
                "asset_name",
                "category",
                "location",
                "department",
                "assigned_on",
            ]
        ].sort_values("assigned_on", ascending=False),
        use_container_width=True
    )

# ─────────────────────────────────────────────
# Assigned Software (TABLE-LIKE + OPEN BUTTON)
# ─────────────────────────────────────────────
st.divider()
st.subheader("💻 Assigned Software")

if software_df.empty:
    st.info("No assigned software found.")
else:
    # Header
    h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
        [1.2, 2, 1.2, 3, 1.8, 1.8, 1.5, 1]
    )

    h1.markdown("**Emp ID**")
    h2.markdown("**Employee Name**")
    h3.markdown("**Soft ID**")
    h4.markdown("**Software Name**")
    h5.markdown("**Department**")
    h6.markdown("**Location**")
    h7.markdown("**Assigned On**")
    h8.markdown("**Action**")

    # Rows
    for i, row in software_df.sort_values(
        "assigned_on", ascending=False
    ).iterrows():

        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
            [1.2, 2, 1.2, 3, 1.8, 1.8, 1.5, 1]
        )

        c1.write(row["employee_id"])
        c2.write(row["employee_name"])
        c3.write(row["soft_id"])
        c4.write(row["soft_name"])
        c5.write(row["department"])
        c6.write(row["location"])
        c7.write(row["assigned_on"])

        if row["links"]:
            c8.link_button("Open", row["links"])
        else:
            c8.write("-")
