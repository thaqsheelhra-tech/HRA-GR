import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from app import get_active_employees, get_db, get_all_employees

st.header("Generate Salary Slip")

emps = get_all_employees()  # allow resigned too for past slips

emp_choice = st.selectbox("Employee", [f"{e['name']} — {e['emp_id']}" for e in emps])
month_offset = st.slider("Month", -12, 0, 0, help="0 = current month")

if emp_choice:
    emp = next(e for e in emps if f"{e['name']} — {e['emp_id']}" == emp_choice)
    target_date = date.today() + relativedelta(months=month_offset)
    month_name = target_date.strftime("%b %Y")

    col1, col2 = st.columns(2)
    basic = col1.number_input("Basic Salary (₹)", value=emp['salary'] or 50000)
    deductions = col2.number_input("Total Deductions (₹)", value=8000, step=500)

    net_pay = basic - deductions

    if st.button("Generate & Download Salary Slip", type="primary"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(w/2, h-80, "Thaqsheel HRMS")
        c.setFont("Helvetica", 12)
        c.drawCentredString(w/2, h-110, f"Salary Slip — {month_name}")

        c.setFont("Helvetica", 11)
        y = h - 180
        data = [
            ("Employee ID", emp['emp_id']),
            ("Name", emp['name']),
            ("Department", emp.get('dept', '—')),
            ("Basic Salary", f"₹ {basic:,.0f}"),
            ("Deductions", f"₹ {deductions:,.0f}"),
            ("Net Pay", f"₹ {net_pay:,.0f}"),
        ]

        for label, value in data:
            c.drawString(100, y, label + ":")
            c.drawRightString(w-100, y, str(value))
            y -= 25

        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(w/2, 60, "This is a computer-generated document — no signature required")
        c.save()

        buffer.seek(0)
        st.download_button(
            label="Download PDF",
            data=buffer,
            file_name=f"Salary_{emp['emp_id']}_{month_name.replace(' ','_')}.pdf",
            mime="application/pdf"
        )
