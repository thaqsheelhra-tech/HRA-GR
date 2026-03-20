import streamlit as st
from datetime import date
from app import get_db

st.header("Onboard New Employee")

with st.form("onboard_form"):
    col1, col2 = st.columns(2)
    name = col1.text_input("Full Name", placeholder="Aarav Sharma")
    email = col2.text_input("Email")

    col1, col2 = st.columns(2)
    dept = col1.selectbox("Department", ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"])
    position = col2.text_input("Position", placeholder="Senior Backend Developer")

    col1, col2, col3 = st.columns(3)
    join_date = col1.date_input("Join Date", value=date.today())
    salary = col2.number_input("Monthly CTC (₹)", min_value=15000, step=5000, value=80000)
    emp_id_prefix = col3.text_input("Emp ID Prefix", value="THQ", max_chars=6)

    submitted = st.form_submit_button("Onboard Employee", type="primary", use_container_width=True)

if submitted:
    if not name.strip():
        st.error("Name is required.")
    else:
        emp_id = f"{emp_id_prefix.upper()}{len(get_all_employees())+1001:04d}"

        with get_db() as conn:
            try:
                conn.execute("""
                    INSERT INTO employees (emp_id, name, email, dept, position, join_date, salary)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (emp_id, name.strip(), email.strip() or None, dept, position.strip(), join_date, salary))
                conn.commit()
                st.success(f"**{name}** onboarded successfully!\nEmployee ID: **{emp_id}**")
            except sqlite3.IntegrityError:
                st.error("Employee ID conflict. Try again.")
