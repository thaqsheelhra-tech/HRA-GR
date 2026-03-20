import streamlit as st
from datetime import date
from app import get_active_employees, get_db

st.header("Leave Management")

tab1, tab2 = st.tabs(["New Request", "All Requests"])

with tab1:
    with st.form("leave_form"):
        emps = get_active_employees()
        emp_choice = st.selectbox("Employee", [f"{e['name']} — {e['emp_id']}" for e in emps])
        leave_type = st.selectbox("Leave Type", ["Casual", "Sick", "Annual", "Maternity", "Other"])
        col1, col2 = st.columns(2)
        start = col1.date_input("Start Date")
        end = col2.date_input("End Date")
        reason = st.text_area("Reason")

        if st.form_submit_button("Submit Leave Request"):
            if start > end:
                st.error("End date cannot be before start date.")
            else:
                days = (end - start).days + 1
                emp_id = emp_choice.split("—")[-1].strip()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO leaves (emp_id, leave_type, start_date, end_date, days, reason, applied_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (emp_id, leave_type, start, end, days, reason, date.today()))
                    conn.commit()
                st.success("Leave request submitted!")

with tab2:
    with get_db() as conn:
        leaves = conn.execute("""
            SELECT l.*, e.name
            FROM leaves l
            JOIN employees e ON l.emp_id = e.emp_id
            ORDER BY l.applied_date DESC
        """).fetchall()

    if not leaves:
        st.info("No leave requests yet.")
    else:
        import pandas as pd
        df = pd.DataFrame([dict(r) for r in leaves])
        st.dataframe(df[["name", "leave_type", "start_date", "end_date", "days", "status"]], use_container_width=True)

        st.subheader("Approve / Reject")
        req_id = st.selectbox("Select request", [r['id'] for r in leaves], format_func=lambda x: f"ID {x}")
        if req_id:
            action = st.radio("Action", ["Approve", "Reject"])
            if st.button("Update Status"):
                new_status = "Approved" if action == "Approve" else "Rejected"
                with get_db() as conn:
                    conn.execute("UPDATE leaves SET status = ? WHERE id = ?", (new_status, req_id))
                    conn.commit()
                st.success(f"Request {req_id} marked as **{new_status}**")
