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
    st.session_state['dev_data'] = pd.DataFrame(dev_data)


# --- REUSABLE FUNCTIONS ---
def display_team_matrix(team_name, df_key):
    st.subheader(f"Update Scores: Canyon {team_name} Team")
    
    df = st.session_state[df_key]
    skill_cols = [col for col in df.columns if col not in ['Name', 'Designation', 'Team/Project']]

    column_config = {
        col: st.column_config.SelectboxColumn(
            col, help="Select score (0 to 4)", options=[0, 1, 2, 3, 4], required=True
        ) for col in skill_cols
    }

    edited_df = st.data_editor(
        df, 
        column_config=column_config, 
        hide_index=True, 
        use_container_width=True, 
        key=f"editor_{team_name}",
        num_rows="fixed" 
    )

    if st.button(f"💾 Save {team_name} Changes", type="primary"):
        edited_df.fillna(0, inplace=True) 
        st.session_state[df_key] = edited_df
        st.session_state['flash_msg'] = f"{team_name} team data saved successfully! Analytics and heatmaps have been updated."
        st.rerun()


def display_admin_controls(team_name, df_key):
    st.divider()
    st.subheader(f"🛠️ Manage {team_name} Structure")
    
    df = st.session_state[df_key]
    
    col1, col2 = st.columns(2)
    
    # --- MANAGE MEMBERS ---
    with col1:
        st.markdown("#### 👤 Team Members")
        with st.form(f"add_member_{team_name}"):
            st.write("**Add New Member**")
            new_name = st.text_input("Member Name")
            new_designation = st.text_input("Designation")
            if st.form_submit_button("➕ Add Member"):
                if new_name:
                    new_row = {'Name': new_name, 'Designation': new_designation}
                    for col in df.columns:
                        if col not in ['Name', 'Designation', 'Team/Project']:
                            new_row[col] = 0
                    
                    st.session_state[df_key] = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state['flash_msg'] = f"Successfully added {new_name} to the {team_name} team!"
                    st.rerun()

        with st.form(f"delete_member_{team_name}"):
            st.write("**Delete Existing Member**")
            member_to_delete = st.selectbox("Select Member to Remove", df['Name'].tolist())
            if st.form_submit_button("❌ Delete Member"):
                if member_to_delete:
                    st.session_state[df_key] = df[df['Name'] != member_to_delete].reset_index(drop=True)
                    st.session_state['flash_msg'] = f"Successfully deleted {member_to_delete} from the {team_name} team."
                    st.rerun()

    # --- MANAGE SKILLS ---
    with col2:
        st.markdown("#### 🎯 Skill Categories")
        with st.form(f"add_skill_{team_name}"):
            st.write("**Add New Skill**")
            new_skill = st.text_input("Skill Name (e.g., React, AWS)")
            if st.form_submit_button("➕ Add Skill"):
                if new_skill and new_skill not in df.columns:
                    st.session_state[df_key][new_skill] = 0
                    st.session_state['flash_msg'] = f"Successfully added the skill '{new_skill}' to the {team_name} matrix!"
                    st.rerun()
                elif new_skill in df.columns:
                    st.session_state['flash_error'] = f"The skill '{new_skill}' already exists!"
                    st.rerun()

        with st.form(f"delete_skill_{team_name}"):
            st.write("**Delete Existing Skill**")
            skills_list = [c for c in df.columns if c not in ['Name', 'Designation', 'Team/Project']]
            skill_to_delete = st.selectbox("Select Skill to Remove", skills_list)
            
            if st.form_submit_button("❌ Delete Skill"):
                if skill_to_delete:
                    st.session_state[df_key] = df.drop(columns=[skill_to_delete])
                    st.session_state['flash_msg'] = f"Successfully removed the skill '{skill_to
