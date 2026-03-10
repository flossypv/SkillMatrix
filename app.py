import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="Canyon Skill Matrix", layout="wide")

# --- DATABASE SETUP (GOOGLE SHEETS) ---
# Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_team_data(team_name, default_data):
    """Fetches data from Google Sheets. If empty, uploads the default data."""
    try:
        # Read the specific tab for the team. ttl=0 ensures we don't cache stale data.
        df = conn.read(worksheet=team_name, ttl=0)
        
        # Clean up any empty trailing columns/rows Google Sheets might append
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        if df.empty:
            df = pd.DataFrame(default_data)
            conn.update(worksheet=team_name, data=df)
        return df
    except Exception as e:
        # If the worksheet is completely blank or errors out, write default data
        df = pd.DataFrame(default_data)
        conn.update(worksheet=team_name, data=df)
        return df

def save_team_data(team_name, df):
    """Saves the DataFrame to the specific Google Sheet tab."""
    conn.update(worksheet=team_name, data=df)


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
    st.title("🔐 Login to Canyon Skill Matrix")
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

st.title("Canyon Skill Matrix")

# --- FLASH MESSAGE SYSTEM ---
if 'flash_msg' in st.session_state:
    st.success(st.session_state['flash_msg'])
    del st.session_state['flash_msg']

if 'flash_error' in st.session_state:
    st.error(st.session_state['flash_error'])
    del st.session_state['flash_error']

# --- INITIALIZE REAL DATA FROM GOOGLE SHEETS ---
default_qa = {
    'Name': ['Dominic Raj', 'Karthika', 'Sangeetha Balajirao', 'Balaji Kupsingh'], 
    'Designation': ['Project Manager', 'Lead Quality Analyst', 'Quality Analyst', 'Quality Analyst'], 
    'Manual': [4, 4, 4, 4], 'Coded Ui': [4, 4, 3, 1], 'Selenium': [4, 3, 1, 3], 'Test Project': [4, 0, 0, 3], 
    'Acceleq': [2, 1, 1, 1], 'Appium': [2, 0, 0, 3], 'Play wright': [2, 0, 0, 1], 'Test Complete': [2, 2, 2, 2], 
    'Jmeter': [3, 2, 2, 3], 'API Automation': [1, 0, 0, 0], 'Postman': [2, 2, 2, 2], 'Java': [3, 3, 2, 3], 
    'C#': [4, 3, 3, 1], 'Phython': [2, 1, 0, 1], 'Azure Test Plan': [4, 4, 2, 3], 'JIRA': [4, 4, 4, 3], 
    'CI-CD Jenkins': [3, 0, 0, 2], 'RPA': [2, 0, 0, 3], 'SQL': [3, 3, 2, 2], 'ETL Testing': [2, 2, 1, 0], 'BI Testing': [3, 4, 0, 1]
}

default_uiux = {
    'Name': ['Ambika', 'Prabavathy'], 
    'Designation': ['Full Stack Developer', 'Frontend Developer'], 
    'PHP': [3, 0], 'Wordpress': [3, 3], 'JavaScript': [3, 2], 'HTML': [3, 3], 'CSS': [2, 3], 'MySQL': [3, 0], 'SQL': [2, 0]
}

default_dev = {
    'Name': ['Prem', 'Arun Menon', 'Rambabu', 'SaiHari', 'Prathap', 'Aravind', 'Ronald'],
    'Designation': ['Project Manager', 'Senior Technical Lead', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Lead Engineer', 'Software Engineer'],
    'Angular': [3, 3, 3, 0, 0, 2, 2], 'C#': [4, 4, 4, 0, 0, 3, 3], 'Database-SQL server': [3, 4, 3, 4, 4, 3, 3],
    'WEB API': [4, 3, 3, 0, 0, 3, 2], 'SSIS': [3, 3, 3, 1, 3, 3, 3], 'Tableau': [0, 0, 0, 4, 3, 0, 0],
    'SSRS': [1, 1, 1, 4, 4, 1, 0], 'Azure Devops': [3, 2, 1, 1, 3, 3, 1], 'MVC': [3, 3, 3, 0, 0, 2, 1],
    'ASPX': [3, 3, 3, 0, 0, 2, 2], 'WCF': [3, 4, 2, 0, 0, 3, 1], 'Win forms': [3, 2, 1, 0, 0, 3, 1],
    'Crystal reports': [1, 0, 1, 0, 0, 0, 0], 'Vb.net': [1, 2, 1, 3, 0, 0, 0], 'Javascript': [3, 3, 3, 0, 0, 3, 3],
    'HTML': [3, 3, 3, 0, 0, 3, 3], 'CSS': [3, 3, 3, 0, 0, 3, 3]
}

if 'qa_data' not in st.session_state:
    st.session_state['qa_data'] = load_team_data("QA", default_qa)

if 'uiux_data' not in st.session_state:
    st.session_state['uiux_data'] = load_team_data("UIUX", default_uiux)

if 'dev_data' not in st.session_state:
    st.session_state['dev_data'] = load_team_data("Dev", default_dev)


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

    if st.button(f"💾 Save {team_name} Changes to Google Sheets", type="primary"):
        edited_df.fillna(0, inplace=True) 
        st.session_state[df_key] = edited_df
        save_team_data(team_name, edited_df) # Syncs to Google Sheets!
        st.session_state['flash_msg'] = f"{team_name} database saved successfully! Analytics and heatmaps have been updated."
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
                    
                    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state[df_key] = updated_df
                    save_team_data(team_name, updated_df) # Sync to Google Sheets
                    st.session_state['flash_msg'] = f"Successfully added {new_name} and synced to database!"
                    st.rerun()

        with st.form(f"delete_member_{team_name}"):
            st.write("**Delete Existing Member**")
            member_to_delete = st.selectbox("Select Member to Remove", df['Name'].tolist())
            if st.form_submit_button("❌ Delete Member"):
                if member_to_delete:
                    updated_df = df[df['Name'] != member_to_delete].reset_index(drop=True)
                    st.session_state[df_key] = updated_df
                    save_team_data(team_name, updated_df) # Sync to Google Sheets
                    st.session_state['flash_msg'] = f"Successfully deleted {member_to_delete} and synced to database."
                    st.rerun()

    # --- MANAGE SKILLS ---
    with col2:
        st.markdown("#### 🎯 Skill Categories")
        with st.form(f"add_skill_{team_name}"):
            st.write("**Add New Skill**")
            new_skill = st.text_input("Skill Name (e.g., React, AWS)")
            if st.form_submit_button("➕ Add Skill"):
                if new_skill and new_skill not in df.columns:
                    df[new_skill] = 0
                    st.session_state[df_key] = df
                    save_team_data(team_name, df) # Sync to Google Sheets
                    st.session_state['flash_msg'] = f"Successfully added '{new_skill}' and synced to database!"
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
                    updated_df = df.drop(columns=[skill_to_delete])
                    st.session_state[df_key] = updated_df
                    save_team_data(team_name, updated_df) # Sync to Google Sheets
                    st.session_state['flash_msg'] = f"Successfully removed '{skill_to_delete}' and synced to database."
                    st.rerun()


def render_heatmap(df_key):
    df = st.session_state[df_key]
    
    # Safely drop columns using errors='ignore' so it never crashes even if columns are missing
    heatmap_data = df.drop(columns=['Designation', 'Team/Project'], errors='ignore')
    skill_cols = [col for col in heatmap_data.columns if col != 'Name']

    def apply_color_logic(val):
        try:
            val = int(float(val)) # Cast to float first in case sheets passes decimals
            if val in [0, 1]: return 'background-color: #F8696B; color: black; font-weight: bold;'
            elif val == 2: return 'background-color: #FFEB84; color: black; font-weight: bold;'
            elif val in [3, 4]: return 'background-color: #63BE7B; color: black; font-weight: bold;'
        except:
            pass
        return ''

    styled_heatmap = heatmap_data.style.map(apply_color_logic, subset=skill_cols)
    st.dataframe(styled_heatmap, use_container_width=True, hide_index=True)


# --- ANALYTICAL VIEW FUNCTION ---
def render_skill_analytics(df_key, team_name):
    st.header(f"📈 {team_name} Team Skill Analytics")
    df = st.session_state[df_key]
    
    exclude_cols = ['Name', 'Designation', 'Team/Project']
    skill_cols = [col for col in df.columns if col not in exclude_cols]
    
    if not skill_cols:
        st.info("No skills available to analyze.")
        return

    # Ensure numeric for calculations
    numeric_df = df.copy()
    for col in skill_cols:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce').fillna(0)
        
    # --- 1. Skill Wise People Score ---
    st.subheader("1. Skill-wise People Score")
    selected_skill = st.selectbox(f"Select a Skill to view all {team_name} member scores:", skill_cols)
    
    skill_scores_df = numeric_df[['Name', selected_skill]].sort_values(by=selected_skill, ascending=False)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(skill_scores_df, hide_index=True, use_container_width=True)
    with col2:
        st.bar_chart(skill_scores_df.set_index('Name'), color="#63BE7B")
        
    st.divider()

    # --- 2. Top 3 Performers per Skill ---
    st.subheader("2. Top 3 Performers per Skill")
    top3_list = []
    for skill in skill_cols:
        sorted_df = numeric_df[['Name', skill]].sort_values(by=skill, ascending=False)
        sorted_df = sorted_df[sorted_df[skill] > 0] 
        
        names = sorted_df['Name'].tolist()
        scores = sorted_df[skill].tolist()
        
        top1 = f"{names[0]} ({scores[0]})" if len(names) > 0 else "-"
        top2 = f"{names[1]} ({scores[1]})" if len(names) > 1 else "-"
        top3 = f"{names[2]} ({scores[2]})" if len(names) > 2 else "-"
        
        top3_list.append({"Skill": skill, "1st Place": top1, "2nd Place": top2, "3rd Place": top3})
        
    st.dataframe(pd.DataFrame(top3_list), hide_index=True, use_container_width=True)
    
    st.divider()

    # --- 3. Zero Skill Details ---
    st.subheader("3. Zero Skill Details (Score = 0)")
    zero_list = []
    for skill in skill_cols:
        zero_members = numeric_df[numeric_df[skill] == 0]['Name'].tolist()
        if zero_members:
            zero_list.append({
                "Skill": skill, 
                "Zero Score Count": len(zero_members),
                "Members with 0 Score": ", ".join(zero_members)
            })
    
    if zero_list:
        st.dataframe(pd.DataFrame(zero_list), hide_index=True, use_container_width=True)
    else:
        st.success("Great job! No one has a zero score in any skill.")


# --- DETERMINE VIEW BASED ON ROLE ---

if st.session_state['team_access'] == 'All':
    tab1, tab2, tab3 = st.tabs(["📝 Master Editor", "📊 Global Heatmaps", "📈 Skill Analytics"])
    
    with tab1:
        st.header("Master Team Matrix Editor")
        selected_team = st.selectbox("Select Team to Edit:", options=["QA", "UI/UX", "Dev"], index=0)
        st.divider()
        
        if selected_team == "QA":
            display_team_matrix("QA", 'qa_data')
            display_admin_controls("QA", 'qa_data')
        elif selected_team == "UI/UX":
            display_team_matrix("UIUX", 'uiux_data')
            display_admin_controls("UIUX", 'uiux_data')
        elif selected_team == "Dev":
            display_team_matrix("Dev", 'dev_data')
            display_admin_controls("Dev", 'dev_data')
            
    with tab2:
        st.header("Global Heatmaps")
        st.markdown("🔴 **0-1**: Beginner | 🟡 **2**: Intermediate | 🟢 **3-4**: Proficient/Expert")
        st.subheader("QA Heatmap")
        render_heatmap('qa_data')
        st.subheader("UI/UX Heatmap")
        render_heatmap('uiux_data')
        st.subheader("Dev Heatmap")
        render_heatmap('dev_data')
        
    with tab3:
        analytics_team = st.selectbox("Select Team for Analytics:", options=["QA", "UI/UX", "Dev"], index=0)
        st.divider()
        if analytics_team == "QA":
            render_skill_analytics('qa_data', "QA")
        elif analytics_team == "UI/UX":
            render_skill_analytics('uiux_data', "UIUX")
        elif analytics_team == "Dev":
            render_skill_analytics('dev_data', "Dev")

# Role specific views
elif st.session_state['team_access'] == 'QA':
    tab1, tab2 = st.tabs(["📝 Update Matrix", "📈 Skill Analytics"])
    with tab1:
        st.info("You are editing the Canyon QA Team Skill Matrix.")
        display_team_matrix("QA", 'qa_data')
    with tab2:
        render_skill_analytics('qa_data', "QA")

elif st.session_state['team_access'] == 'UIUX':
    tab1, tab2 = st.tabs(["📝 Update Matrix", "📈 Skill Analytics"])
    with tab1:
        st.info("You are editing the Canyon UI/UX Team Skill Matrix.")
        display_team_matrix("UIUX", 'uiux_data')
    with tab2:
        render_skill_analytics('uiux_data', "UIUX")

elif st.session_state['team_access'] == 'Dev':
    tab1, tab2 = st.tabs(["📝 Update Matrix", "📈 Skill Analytics"])
    with tab1:
        st.info("You are editing the Canyon Dev Team Skill Matrix.")
        display_team_matrix("Dev", 'dev_data')
    with tab2:
        render_skill_analytics('dev_data', "Dev")
