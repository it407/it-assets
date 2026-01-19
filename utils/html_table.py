import streamlit as st
import pandas as pd

def render_html_table(
    df: pd.DataFrame,
    columns: list,
    link_column: str | None = None,
    link_label: str = "Open",
):
    if df.empty:
        st.info("No data available.")
        return

    # Ensure columns exist
    columns = [c for c in columns if c in df.columns]

    html = """
    <style>
        .table-wrapper {
            width: 100%;
            overflow-x: auto;
        }

        table.custom-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            min-width: 700px;
        }

        table.custom-table th,
        table.custom-table td {
            border: 1px solid #ddd;
            padding: 8px;
            white-space: nowrap;
        }

        table.custom-table th {
            background-color: #f4f6f8;
            font-weight: 600;
            text-align: left;
        }

        table.custom-table tr:nth-child(even) {
            background-color: #fafafa;
        }

        a.open-btn {
            padding: 4px 10px;
            background-color: #0f62fe;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 13px;
        }

        a.open-btn:hover {
            background-color: #0043ce;
        }
    </style>

    <div class="table-wrapper">
    <table class="custom-table">
        <thead>
            <tr>
    """

    for col in columns:
        html += f"<th>{col.replace('_', ' ').title()}</th>"

    if link_column:
        html += "<th>Action</th>"

    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"

        for col in columns:
            val = "" if pd.isna(row[col]) else row[col]
            html += f"<td>{val}</td>"

        if link_column:
            link = row.get(link_column)
            if pd.notna(link) and str(link).strip():
                html += (
                    f'<td><a class="open-btn" href="{link}" '
                    f'target="_blank">{link_label}</a></td>'
                )
            else:
                html += "<td>-</td>"

        html += "</tr>"

    html += "</tbody></table></div>"

    st.markdown(html, unsafe_allow_html=True)
