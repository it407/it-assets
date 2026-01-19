import streamlit as st

def render_software_cards(df):
    css = """
    <style>
    .soft-card {
        background: #0e1117;
        border: 1px solid #262730;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
        display: grid;
        grid-template-columns: 1.2fr 2fr 1.2fr 2.5fr 1.5fr 1.5fr 1.2fr 1fr;
        gap: 10px;
        align-items: center;
        color: #fafafa;
    }

    .soft-header {
        font-weight: 600;
        color: #9aa0a6;
        font-size: 13px;
        padding-bottom: 6px;
    }

    .soft-link a {
        text-decoration: none;
        color: #00c2ff;
        font-weight: 500;
    }

    .soft-link a:hover {
        text-decoration: underline;
    }

    .soft-muted {
        color: #8b949e;
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    # Header row
    header = """
    <div class="soft-card soft-header">
        <div>Emp ID</div>
        <div>Employee</div>
        <div>Soft ID</div>
        <div>Software</div>
        <div>Department</div>
        <div>Location</div>
        <div>Assigned On</div>
        <div>Link</div>
    </div>
    """
    st.markdown(header, unsafe_allow_html=True)

    # Data rows
    for _, r in df.iterrows():
        link_html = (
            f'<a href="{r["links"]}" target="_blank">Open</a>'
            if r["links"] else "-"
        )

        row_html = f"""
        <div class="soft-card">
            <div>{r["employee_id"]}</div>
            <div>{r["employee_name"]}</div>
            <div>{r["soft_id"]}</div>
            <div>{r["soft_name"]}</div>
            <div>{r["department"]}</div>
            <div>{r["location"]}</div>
            <div class="soft-muted">{r["assigned_on"]}</div>
            <div class="soft-link">{link_html}</div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
