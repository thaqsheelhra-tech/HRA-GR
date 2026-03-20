import streamlit as st
from app import get_active_employees, get_db

st.header("Process Resignation")

emps = get_active_employees()

if not emps:
    st.info("No active employees.")
else:
    options = [f"{e['name']}  —  {e['emp_id']}" for e in emps]
    choice = st.selectbox("Select employee", options)

    if choice:
        emp = next(e for e in emps if f"{e['name']}  —  {e['emp_id']}" == choice)
        last_day = st.date_input("Last working day", value=date.today() + relativedelta(months=1))

        reason = st.selectbox("Reason", [
            "Better opportunity", "Personal reasons", "Relocation",
            "Health", "Family", "Higher studies", "Other"
        ])

        if st.button("Confirm Resignation", type="primary"):
            with get_db() as conn:
                conn.execute("UPDATE employees SET status = 'Resigned' WHERE emp_id = ?", (emp['emp_id'],))
                conn.commit()
            st.success(f"Resignation processed for **{emp['name']}**.\nLast day: {last_day}")
