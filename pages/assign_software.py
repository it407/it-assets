import streamlit as st
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, append_row
from utils.auth import logout

admin_only()
logout()

st.title("🔗 Assign Software")

soft_df = read_sheet("software_master")
emp_df = read_sheet("employee_master")
assign_df = read_sheet("software_assignments")

for df in [soft_df, emp_df, assign_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

active_soft = soft_df[soft_df["status"] == "Active"]

if active_soft.empty:
    st.warning("No active software available")
    st.stop()

soft_map = {
    f"{r['soft_id']} | {r['soft_name']}": r
    for _, r in active_soft.iterrows()
}

emp_map = {
    f"{r['employee_id']} | {r['employee_name']}": r
    for _, r in emp_df.iterrows()
}

def next_assign_id(df):
    if df.empty:
        return "SASN-001"
    nums = (
        df["assignment_id"]
        .astype(str)
        .str.replace("SASN-", "", regex=False)
        .astype(int)
    )
    return f"SASN-{str(nums.max()+1).zfill(3)}"

with st.form("assign_soft_form"):
    soft_sel = st.selectbox("Software *", list(soft_map.keys()))
    emp_sel = st.selectbox("Employee *", list(emp_map.keys()))
    remarks = st.text_input("Remarks")

    submit = st.form_submit_button("Assign")

if submit:
    now = datetime.now().isoformat()

    append_row(
        "software_assignments",
        {
            "assignment_id": next_assign_id(assign_df),
            "soft_id": soft_map[soft_sel]["soft_id"],
            "soft_name": soft_map[soft_sel]["soft_name"],
            "employee_id": emp_map[emp_sel]["employee_id"],
            "employee_name": emp_map[emp_sel]["employee_name"],
            "assigned_on": now,
            "returned_on": "",
            "assignment_status": "Assigned",
            "remarks": remarks,
            "created_at": now,
        }
    )

    st.success("Software assigned successfully")
    st.rerun()
