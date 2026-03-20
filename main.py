import streamlit as st
import sqlite3
import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

# ────────────────────────────────────────────────
#  CONFIG
# ────────────────────────────────────────────────

DB_FILE = "hrms.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="Thaqsheel HRMS",
    page_icon="👩‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
#  DB HELPERS
# ────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            dept TEXT,
            position TEXT,
            join_date DATE,
            salary INTEGER,
            status TEXT DEFAULT 'Active'
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            att_date DATE,
            status TEXT,                -- Present / Absent / Half-day / Leave
            FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            leave_type TEXT,
            start_date DATE,
            end_date DATE,
            days INTEGER,
            reason TEXT,
            status TEXT DEFAULT 'Pending',   -- Pending / Approved / Rejected
            applied_date DATE,
            FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            title TEXT,
            uploaded_at DATE
        )''')

        conn.commit()

# Run once
if not os.path.exists(DB_FILE):
    init_db()

# ────────────────────────────────────────────────
#  SIDEBAR & HEADER
# ────────────────────────────────────────────────

st.sidebar.title("Thaqsheel HRMS")
st.sidebar.markdown(f"**Today:** {date.today().strftime('%d %b %Y')}")

page = st.sidebar.radio("Main Menu", [
    "🏠 Dashboard",
    "📋 Employees",
    "➕ Onboard Employee",
    "➖ Resignation",
    "📄 Policies & Documents",
    "🕒 Attendance",
    "🌴 Leave Management",
    "💰 Salary Slips"
], index=0)

st.title(page)

# ────────────────────────────────────────────────
#  SHARED QUERIES
# ────────────────────────────────────────────────

def get_all_employees():
    with get_db() as conn:
        df = conn.execute("""
            SELECT emp_id, name, dept, position, join_date, salary, status
            FROM employees
            ORDER BY name
        """).fetchall()
    return [dict(row) for row in df]

def get_active_employees():
    return [e for e in get_all_employees() if e['status'] == 'Active']

# ────────────────────────────────────────────────
#  DASHBOARD
# ────────────────────────────────────────────────

if page == "🏠 Dashboard":
    st.header("Overview")

    employees = get_all_employees()
    active = len([e for e in employees if e['status'] == 'Active'])
    resigned = len([e for e in employees if e['status'] == 'Resigned'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", len(employees))
    col2.metric("Active", active, delta_color="normal")
    col3.metric("Resigned", resigned, delta_color="inverse")

    st.subheader("Recent Activity")
    st.info("This is a minimal dashboard. More stats can be added later (attendance %, pending leaves, etc.)")
