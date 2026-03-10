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

# --- INITIALIZE REAL DATA ---
if 'qa_data' not in st.session_state:
    qa_data = {
        'Name': ['Dominic Raj', 'Karthika', 'Sangeetha Balajirao', 'Balaji Kupsingh'], 
        'Designation': ['Project Manager', 'Lead Quality Analyst', 'Quality Analyst', 'Quality Analyst'], 
        'Manual': [4, 4, 4, 4], 'Coded Ui': [4, 4, 3, 1], 'Selenium': [4, 3, 1, 3], 'Test Project': [4, 0, 0, 3], 
        'Acceleq': [2, 1, 1, 1], 'Appium': [2, 0, 0, 3], 'Play wright': [2, 0, 0, 1], 'Test Complete': [2, 2, 2, 2], 
        'Jmeter': [3, 2, 2, 3], 'API Automation': [1, 0, 0, 0], 'Postman': [2, 2, 2, 2], 'Java': [3, 3, 2, 3], 
        'C#': [4, 3, 3, 1], 'Phython': [2, 1, 0, 1], 'Azure Test Plan': [4, 4, 2, 3], 'JIRA': [4, 4, 4, 3], 
        'CI-CD Jenkins': [3, 0, 0, 2], 'RPA': [2, 0, 0, 3], 'SQL': [3, 3, 2, 2], 'ETL Testing': [2, 2, 1, 0], 'BI Testing': [3, 4, 0, 1]
    }
    st.session_state['qa_data'] = pd.DataFrame(qa_data)

if 'uiux_data' not in st.session_state:
    uiux_data = {
        'Name': ['Ambika', 'Prabavathy'], 
        'Designation': ['Full Stack Developer', 'Frontend Developer'], 
        'PHP': [3, 0], 'Wordpress': [3, 3], 'JavaScript': [3, 2], 'HTML': [3, 3], 'CSS': [2, 3], 'MySQL': [3, 0], 'SQL': [2, 0]
    }
    st.session_state['uiux_data'] = pd.DataFrame(uiux_data)

if 'dev_data' not in st.session_state:
    dev_data = {
        'Name': ['Prem', 'Arun Menon', 'Rambabu', 'SaiHari', 'Prathap', 'Aravind', 'Ronald'],
        'Designation': ['Project Manager', 'Senior Technical Lead', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Software Engineer'],
        'Angular': [3, 3, 3, 0, 0, 2, 2], 'C#': [4, 4, 4, 0, 0, 3, 3], 'Database-SQL server': [3, 4, 3, 4, 4, 3, 3],
        'WEB API': [4, 3, 3, 0, 0, 3, 2], 'SSIS': [3, 3, 3, 1, 3, 3, 3], 'Tableau': [0, 0, 0, 4, 3, 0, 0],
        'SSRS': [1, 1, 1, 4, 4, 1, 0], 'Azure Devops': [3, 2, 1, 1, 3, 3, 1], 'MVC': [3, 3, 3, 0, 0, 2, 1],
        'ASPX': [3, 3, 3, 0, 0, 2, 2], 'WCF': [3, 4, 2, 0, 0, 3, 1], 'Win forms': [3, 2, 1, 0, 0, 3, 1],
        'Crystal reports': [1, 0, 1, 0, 0, 0, 0], 'Vb.net': [1, 2, 1, 3, 0, 0, 0], 'Javascript': [3, 3, 3, 0, 0, 3, 3],
        'HTML': [3, 3, 3, 0, 0, 3, 3], 'CSS': [3, 3, 3, 0, 0, 3, 3]
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

    st.session_state[df_key] = st.data_editor(
        df, column_config=column_config, hide_index=True, use_container_width=True, key=f"editor_{team_name}"
    )

def render_heatmap(df_key):
    df = st.session_state[df_key]
    heatmap_data = df.set_index('Name').drop(columns=[col for col in ['Designation', 'Team/Project'] if col in df.columns])

    def apply_color_logic(val):
        if val in [0, 1]: return 'background-color: #F8696B; color: black; font-weight: bold;'
        elif val == 2: return 'background-color: #FFEB84; color: black; font-weight: bold;'
        elif val in [3, 4]: return 'background-color: #63BE7B; color: black; font-weight: bold;'
        return ''

    styled_heatmap = heatmap_data.style.map(apply_color_logic)
    st.dataframe(styled_heatmap, use_container_width=True)


# --- DETERMINE VIEW BASED ON ROLE ---

# 1. ADMIN VIEW (Sees All Teams via Tabs)
if st.session_state['team_access'] == 'All':
    tab1, tab2, tab3, tab4 = st.tabs(["📝 QA Team Matrix", "📝 UI/UX Team Matrix", "📝 Dev Team Matrix", "📊 Global Heatmaps"])
    
    with tab1:
        display_team_matrix("QA", 'qa_data')
    with tab2:
        display_team_matrix("UI/UX", 'uiux_data')
    with tab3:
        display_team_matrix("Dev", 'dev_data')
    with tab4:
        st.header("Global Heatmaps (Admin View)")
        st.markdown("🔴 **0-1**: Beginner | 🟡 **2**: Intermediate | 🟢 **3-4**: Proficient/Expert")
        
        st.subheader("Canyon QA Heatmap")
        render_heatmap('qa_data')
        
        st.divider()
        st.subheader("Canyon UI/UX Heatmap")
        render_heatmap('uiux_data')

        st.divider()
        st.subheader("Canyon Dev Heatmap")
        render_heatmap('dev_data')

# 2. QA TEAM VIEW 
elif st.session_state['team_access'] == 'QA':
    st.info("You are editing the Canyon QA Team Skill Matrix.")
    display_team_matrix("QA", 'qa_data')

# 3. UI/UX TEAM VIEW 
elif st.session_state['team_access'] == 'UIUX':
    st.info("You are editing the Canyon UI/UX Team Skill Matrix.")
    display_team_matrix("UI/UX", 'uiux_data')

# 4. DEV TEAM VIEW 
elif st.session_state['team_access'] == 'Dev':
    st.info("You are editing the Canyon Dev Team Skill Matrix.")
    display_team_matrix("Dev", 'dev_data')
