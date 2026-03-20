import streamlit as st
from app import get_db, get_all_employees

st.header("Employee Directory")

data = get_all_employees()

if not data:
    st.info("No employees yet. Onboard someone first.")
else:
    import pandas as pd
    df = pd.DataFrame(data)
    st.dataframe(
        df.style.format({"salary": "₹ {:,}", "join_date": "{}"}),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Quick Actions")
    emp_id = st.selectbox("Select employee to view / edit", [e['emp_id'] for e in data], key="emp_select")

    if emp_id:
        emp = next(e for e in data if e['emp_id'] == emp_id)
        with st.expander(f"Details — {emp['name']} ({emp_id})", expanded=True):
            st.write(emp)
