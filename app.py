import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Skill Matrix", layout="wide")

# --- DUMMY USER DATABASE ---
# In a real app, you would use a database and hashed passwords.
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "employee": {"password": "user123", "role": "user"}
}

# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None

# --- LOGIN PAGE ---
if not st.session_state['authenticated']:
    st.title("🔐 Login to Skill Matrix")
    st.write("Please log in to continue.")
    
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
                st.rerun() # Refresh the page to load the main app
            else:
                st.error("Invalid username or password")
    
    # Stop the script here so the rest of the app doesn't load if not logged in
    st.stop()


# --- MAIN APP (Only runs if authenticated) ---

# Sidebar for Logout and User Info
st.sidebar.title("Profile")
st.sidebar.write(f"**Logged in as:** {st.session_state['username']}")
st.sidebar.write(f"**Role:** {st.session_state['role'].capitalize()}")

if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.rerun()

st.title("Interactive Skill Matrix")

# Initialize Data in Session State
if 'skill_data' not in st.session_state:
    data = {
        'Name': ['Prem', 'Arun Menon', 'Rambabu', 'SaiHari', 'Prathap', 'Aravind', 'Ronald'],
        'Designation': ['Project Manager', 'Senior Technical Lead', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Software Engineer'],
        'Angular': [3, 3, 3, 0, 0, 2, 2],
        'C#': [4, 4, 4, 0, 0, 3, 3],
        'Database-SQL server': [3, 4, 3, 4, 4, 3, 3],
        'WEB API': [4, 3, 3, 0, 0, 3, 2],
        'SSIS': [3, 3, 3, 1, 3, 3, 3],
        'Tableau': [0, 0, 0, 4, 3, 0, 0],
        'SSRS': [1, 1, 1, 4, 4, 1, 0],
        'Azure Devops': [3, 2, 1, 1, 3, 3, 1],
        'MVC': [3, 3, 3, 0, 0, 2, 1],
        'ASPX': [3, 3, 3, 0, 0, 2, 2],
        'WCF': [3, 4, 2, 0, 0, 3, 1],
        'Win forms': [3, 2, 1, 0, 0, 3, 1],
        'Crystal reports': [1, 0, 1, 0, 0, 0, 0],
        'Vb.net': [1, 2, 1, 3, 0, 0, 0],
        'Javascript': [3, 3, 3, 0, 0, 3, 3],
        'HTML': [3, 3, 3, 0, 0, 3, 3],
        'CSS': [3, 3, 3, 0, 0, 3, 3]
    }
    st.session_state['skill_data'] = pd.DataFrame(data)

# --- ROLE-BASED TAB DISPLAY ---
# If admin, show both tabs. If user, only show the first tab.
if st.session_state['role'] == 'admin':
    tabs = st.tabs(["📝 Data Entry & Definitions", "📊 Heatmap Dashboard"])
    tab1 = tabs[0]
    tab2 = tabs[1]
else:
    tabs = st.tabs(["📝 Data Entry & Definitions"])
    tab1 = tabs[0]
    tab2 = None # No tab 2 for standard users

with tab1:
    st.header("Skill Level Definitions")
    st.markdown("""
    | Score | Skill Level | Description |
    | :--- | :--- | :--- |
    | **4** | **Expert** | Fully Capable & Experienced. Needs no assistance. |
    | **3** | **Proficient** | Capable & Experienced. Able to work independently. |
    | **2** | **Intermediate** | Able to perform. Needs help from time to time. |
    | **1** | **Beginner** | Limited Knowledge. Needs significant help. |
    | **0** | **No Knowledge** | No knowledge & Experience. |
    """)
    
    st.divider()
    st.subheader("Update Team Scores")
    
    df = st.session_state['skill_data']
    skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]

    column_config = {
        col: st.column_config.SelectboxColumn(
            col, help="Select score (0 to 4)", options=[0, 1, 2, 3, 4], required=True
        ) for col in skill_cols
    }

    # Save edits directly back to session state so they persist
    st.session_state['skill_data'] = st.data_editor(
        df, 
        column_config=column_config, 
        hide_index=True,
        use_container_width=True,
        height=300
    )

# Only attempt to render the Heatmap tab if the user is an admin
if tab2 is not None:
    with tab2:
        st.header("Team Heatmap (Admin View)")
        st.markdown("🔴 **0-1**: Beginner | 🟡 **2**: Intermediate | 🟢 **3-4**: Proficient/Expert")
        
        heatmap_data = st.session_state['skill_data'].set_index('Name').drop(columns=['Designation'])

        def apply_color_logic(val):
            if val in [0, 1]:
                return 'background-color: #F8696B; color: black; font-weight: bold;'
            elif val == 2:
                return 'background-color: #FFEB84; color: black; font-weight: bold;'
            elif val in [3, 4]:
                return 'background-color: #63BE7B; color: black; font-weight: bold;'
            return ''

        styled_heatmap = heatmap_data.style.map(apply_color_logic)
        st.dataframe(styled_heatmap, use_container_width=True, height=400)
