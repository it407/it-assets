from utils.html_table import render_html_table

render_html_table(
    df=software_df,
    columns=[
        "employee_id",
        "employee_name",
        "soft_id",
        "soft_name",
        "department",
        "location",
        "assigned_on",
    ],
    link_column="links",
)
