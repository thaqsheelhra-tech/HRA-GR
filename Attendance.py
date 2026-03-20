import streamlit as st
from datetime import date
from app import get_active_employees, get_db

st.header("Mark Today's Attendance")

today = date.today().isoformat()
emps = get_active_employees()

if not emps:
    st.info("No active employees.")
else:
    with st.form("attendance_form"):
        att_data = {}
        for emp in emps:
            att_data[emp['emp_id']] = st.radio(
                f"{emp['name']} ({emp['emp_id']})",
                ["Present", "Absent", "Half-day", "Leave"],
                horizontal=True,
                key=f"att_{emp['emp_id']}"
            )

        submitted = st.form_submit_button("Save Attendance", type="primary")

    if submitted:
        with get_db() as conn:
            for emp_id, status in att_data.items():
                conn.execute("""
                    INSERT OR REPLACE INTO attendance (emp_id, att_date, status)
                    VALUES (?, ?, ?)
                """, (emp_id, today, status))
            conn.commit()
        st.success(f"Attendance saved for {today}")
