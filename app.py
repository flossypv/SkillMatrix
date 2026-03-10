import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Skill Matrix Dashboard", layout="wide")

# --- USER DATABASE & ROLES ---
USERS = {
    "admin": {"password": "admin123$", "role": "admin", "team": "All"},
    "canyonqa": {"password": "qa123$", "role": "editor", "team": "QA"},
    "canyonuiux": {"password": "uiux123$", "role": "editor", "team": "UIUX"},
    "canyondev": {"password": "dev123$", "role": "editor", "team": "Dev"}
}

# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['team_access'] = None

# --- LOGIN PAGE ---
if not st.session_state['authenticated']:
    st.title("🔐 Login to Skill Matrix Dashboard")
    st.write("Please log in to manage your team's skill matrix.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            user_info = USERS.get(username)
            if user_info and user_info['password'] == password:
                st.session_state['authenticated'] = True
                st.session_state['role'] = user_info['role']
                st.session_state['username'] = username
                st.session_state['team_access'] = user_info['team']
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.stop()


# --- MAIN APP ROUTING ---

# Sidebar Profile & Logout
st.sidebar.title("Profile")
st.sidebar.write(f"**User:** {st.session_state['username']}")
st.sidebar.write(f"**Team Access:** {st.session_state['team_access']}")

if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['team_access'] = None
    st.rerun()

st.title("Interactive Skill Matrix")

# --- FLASH MESSAGE SYSTEM ---
if 'flash_msg' in st.session_state:
    st.success(st.session_state['flash_msg'])
    del st.session_state['flash_msg']

if 'flash_error' in st.session_state:
    st.error(st.session_state['flash_error'])
    del st.session_state['flash_error']

# --- INITIALIZE REAL DATA ---
if 'qa_data' not in st.session_state:
    qa_data = {
        'Name': ['Dominic Raj', 'Karthika', 'Sangeetha Balajirao', 'Balaji Kupsingh'], 
        'Designation': ['Project Manager', 'Lead Quality Analyst', 'Quality Analyst', 'Quality Analyst'], 
        'Manual': [4, 4, 4, 4], 
        'Coded Ui': [4, 4, 3, 1], 
        'Selenium': [4, 3, 1, 3], 
        'Test Project': [4, 0, 0, 3], 
        'Acceleq': [2, 1, 1, 1], 
        'Appium': [2, 0, 0, 3], 
        'Play wright': [2, 0, 0, 1], 
        'Test Complete': [2, 2, 2, 2], 
        'Jmeter': [3, 2, 2, 3], 
        'API Automation': [1, 0, 0, 0], 
        'Postman': [2, 2, 2, 2], 
        'Java': [3, 3, 2, 3], 
        'C#': [4, 3, 3, 1], 
        'Phython': [2, 1, 0, 1], 
        'Azure Test Plan': [4, 4, 2, 3], 
        'JIRA': [4, 4, 4, 3], 
        'CI-CD Jenkins': [3, 0, 0, 2], 
        'RPA': [2, 0, 0, 3], 
        'SQL': [3, 3, 2, 2], 
        'ETL Testing': [2, 2, 1, 0], 
        'BI Testing': [3, 4, 0, 1]
    }
    st.session_state['qa_data'] = pd.DataFrame(qa_data)

if 'uiux_data' not in st.session_state:
    uiux_data = {
        'Name': ['Ambika', 'Prabavathy'], 
        'Designation': ['Full Stack Developer', 'Frontend Developer'], 
        'PHP': [3, 0], 
        'Wordpress': [3, 3], 
        'JavaScript': [3, 2], 
        'HTML': [3, 3], 
        'CSS': [2, 3], 
        'MySQL': [3, 0], 
        'SQL': [2, 0]
    }
    st.session_state['uiux_data'] = pd.DataFrame(uiux_data)

if 'dev_data' not in st.session_state:
    dev_data = {
        'Name': ['Prem', 'Arun Menon', 'Rambabu', 'SaiHari', 'Prathap', 'Aravind', 'Ronald'],
        'Designation': ['Project Manager', 'Senior Technical Lead', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Software Engineer'],
        'Angular': [3, 3, 3, 0, 0, 2, 2], 
        'C#': [4, 4, 4, 0, 0, 3, 3], 
        'Database-SQL server': [3, 4, 3, 4, 4, 3, 3
