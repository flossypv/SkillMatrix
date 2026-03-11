import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials

# 1. Page Configuration
st.set_page_config(page_title="Canyon SkillMatrix", layout="wide", initial_sidebar_state="expanded")

# --- DATABASE SETUP (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Default Data Sets
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

def ensure_worksheet_exists(sheet_name):
    """Uses Google API to silently create a new tab in Google Sheets if it doesn't exist."""
    try:
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        url = secrets_dict.pop("spreadsheet", None) 
        creds = Credentials.from_service_account_info(
            secrets_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_url(url)
        try:
            sh.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            sh.add_worksheet(title=sheet_name, rows=100, cols=20)
    except Exception:
        pass


# --- DYNAMIC CREDENTIALS MANAGEMENT ---
def load_credentials():
    """Loads login credentials from Google Sheets."""
    try:
        df = conn.read(worksheet="Credentials", ttl=0).dropna(how='all')
        if df.empty: raise Exception("Empty Credentials")
        return df
    except Exception:
        default_users = pd.DataFrame({
            "Username": ["superadmin", "canyonadmin", "canyonqa", "canyonuiux", "canyondev"],
            "Password": ["super123$", "admin123$", "qa123$", "uiux123$", "dev123$"],
            "Role": ["superadmin", "admin", "editor", "editor", "editor"],
            "Team": ["All", "Canyon", "Canyon", "Canyon", "Canyon"],
            "Department": ["All", "All", "QA", "UIUX", "Dev"]
        })
        ensure_worksheet_exists("Credentials")
        conn.update(worksheet="Credentials", data=default_users)
        return default_users

def add_credential(username, password, role, team, dept):
    creds_df = load_credentials()
    if username in creds_df['Username'].astype(str).values:
        return False
    
    new_user = pd.DataFrame([{"Username": username, "Password": password, "Role": role, "Team": team, "Department": dept}])
    updated_creds = pd.concat([creds_df, new_user], ignore_index=True)
    conn.update(worksheet="Credentials", data=updated_creds)
    return True

def delete_credential(username):
    creds_df = load_credentials()
    updated_creds = creds_df[creds_df['Username'].astype(str) != str(username)]
    conn.update(worksheet="Credentials", data=updated_creds)


# --- DIRECTORY AND MATRIX MANAGEMENT ---
def load_directory():
    try:
        df = conn.read(worksheet="Directory", ttl=0).dropna(how='all')
        if df.empty: raise Exception("Empty Directory")
        return df
    except Exception:
        default_dir = pd.DataFrame({"Team": ["Canyon", "Canyon", "Canyon"], "Department": ["QA", "UIUX", "Dev"]})
        ensure_worksheet_exists("Directory")
        conn.update(worksheet="Directory", data=default_dir)
        return default_dir

def get_sheet_name(team, dept):
    return str(team) if str(dept) == "None" else f"{team}_{dept}"

def get_display_name(team, dept):
    return str(team) if str(dept) == "None" else f"{team} - {dept}"

def load_matrix(team, dept):
    sheet_name = get_sheet_name(team, dept)
    try:
        df = conn.read(worksheet=sheet_name, ttl=0).dropna(how='all', axis=1).dropna(how='all', axis=0)
        if df.empty: raise Exception("Empty Matrix")
    except Exception:
        if str(team) == "Canyon" and str(dept) == "QA": df = pd.DataFrame(default_qa)
        elif str(team) == "Canyon" and str(dept) == "UIUX": df = pd.DataFrame(default_uiux)
        elif str(team) == "Canyon" and str(dept) == "Dev": df = pd.DataFrame(default_dev)
        else: df = pd.DataFrame(columns=['Name', 'Designation'])
        
        ensure_worksheet_exists(sheet_name)
        conn.update(worksheet=sheet_name, data=df)
        
    for col in df.columns:
        if col not in ['Name', 'Designation']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    return df

def save_matrix(team, dept, df):
    sheet_name = get_sheet_name(team, dept)
    conn.update(worksheet=sheet_name, data=df)

def add_to_directory(team, dept):
    dir_df = load_directory()
    if not ((dir_df['Team'].astype(str) == str(team)) & (dir_df['Department'].astype(str) == str(dept))).any():
        new_row = pd.DataFrame([{"Team": str(team), "Department": str(dept)}])
        updated_dir = pd.concat([dir_df, new_row], ignore_index=True)
        conn.update(worksheet="Directory", data=updated_dir)
        
        sheet_name = get_sheet_name(team, dept)
        empty_df = pd.DataFrame(columns=['Name', 'Designation'])
        ensure_worksheet_exists(sheet_name)
        conn.update(worksheet=sheet_name, data=empty_df)

def delete_from_directory(team, dept):
    dir_df = load_directory()
    updated_dir = dir_df[~((dir_df['Team'].astype(str) == str(team)) & (dir_df['Department'].astype(str) == str(dept)))]
    conn.update(worksheet="Directory", data=updated_dir)


# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['team_access'] = None
    st.session_state['dept_access'] = None

# --- BEAUTIFUL LOGIN PAGE ---
if not st.session_state['authenticated']:
    # Use columns to split the page: 55% left, 10% spacing, 35% right
    col_info, col_space, col_login = st.columns([1.3, 0.2, 0.9])
    
    with col_info:
        st.title("Canyon SkillMatrix 🚀")
        st.markdown("""
        #### Empowering Teams Through Skill Tracking
        Track, analyze, and manage your organization's capabilities securely with our dynamic dashboard.
        
        * 📊 **Interactive Heatmaps:** Instantly spot skill gaps and strengths.
        * 📈 **Deep Analytics:** Identify top performers and training opportunities.
        * 🏢 **Custom Hierarchies:** Tailor the matrix to your exact team structure.
        * 🔐 **Role-Based Access:** Secure, specific views for Admins and Editors.
        """)
        st.write("") # small gap
        # Add a nice open-source infographic image
        st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", use_container_width=True)

    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True) # Push the form down to align better
        st.subheader("🔐 Secure Login")
        st.write("Please log in to manage your team.")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            # Make the button wide for a modern look
            submit = st.form_submit_button("Log In", use_container_width=True)

            if submit:
                creds_df = load_credentials()
                user_row = creds_df[creds_df['Username'].astype(str) == str(username)]
                
                if not user_row.empty and str(user_row.iloc[0]['Password']) == password:
                    st.session_state['authenticated'] = True
                    st.session_state['role'] = str(user_row.iloc[0]['Role'])
                    st.session_state['username'] = str(username)
                    st.session_state['team_access'] = str(user_row.iloc[0]['Team'])
                    st.session_state['dept_access'] = str(user_row.iloc[0]['Department'])
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    # Stop execution here so the rest of the app doesn't load
    st.stop()


# --- MAIN APP ROUTING ---

st.sidebar.title("Profile")
st.sidebar.write(f"**User:** {st.session_state['username']}")
if st.session_state['role'] == 'superadmin':
    st.sidebar.write("**Access:** Superadmin")
elif st.session_state['role'] == 'admin':
    st.sidebar.write(f"**Access:** Team Admin ({st.session_state['team_access']})")
else:
    st.sidebar.write(f"**Team:** {st.session_state['team_access']}")
    if st.session_state['dept_access'] != "None":
        st.sidebar.write(f"**Department:** {st.session_state['dept_access']}")

if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['team_access'] = None
    st.session_state['dept_access'] = None
    st.rerun()

st.title("Canyon SkillMatrix")

if 'flash_msg' in st.session_state:
    st.success(st.session_state['flash_msg'])
    del st.session_state['flash_msg']
if 'flash_error' in st.session_state:
    st.error(st.session_state['flash_error'])
    del st.session_state['flash_error']


# --- REUSABLE UI FUNCTIONS ---
def display_team_matrix(team, dept, df_key):
    disp_name = get_display_name(team, dept)
    st.subheader(f"Update Scores: {disp_name}")
    
    df = st.session_state[df_key]
    skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]

    column_config = {
        col: st.column_config.SelectboxColumn(col, options=[0, 1, 2, 3, 4], required=True) 
        for col in skill_cols
    }

    edited_df = st.data_editor(df, column_config=column_config, hide_index=True, use_container_width=True, key=f"editor_{team}_{dept}", num_rows="fixed")

    if st.button("💾 Save Changes", type="primary", key=f"save_btn_{team}_{dept}"):
        edited_df.fillna(0, inplace=True) 
        for col in skill_cols:
            edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0).astype(int)
            
        st.session_state[df_key] = edited_df
        save_matrix(team, dept, edited_df)
        st.session_state['flash_msg'] = f"{disp_name} database saved successfully!"
        st.rerun()

def display_admin_controls(team, dept, df_key):
    disp_name = get_display_name(team, dept)
    st.divider()
    st.subheader(f"🛠️ Manage Structure: {disp_name}")
    
    df = st.session_state[df_key]
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Members")
        with st.form(f"add_member_{team}_{dept}", clear_on_submit=True):
            new_name = st.text_input("Member Name")
            new_designation = st.text_input("Designation")
            if st.form_submit_button("➕ Add Member"):
                if new_name:
                    new_row = {'Name': new_name, 'Designation': new_designation}
                    for col in df.columns:
                        if col not in ['Name', 'Designation']: new_row[col] = 0
                    
                    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state[df_key] = updated_df
                    save_matrix(team, dept, updated_df)
                    st.session_state['flash_msg'] = f"Successfully added {new_name}!"
                    st.rerun()

        with st.form(f"delete_member_{team}_{dept}"):
            member_to_delete = st.selectbox("Select Member to Remove", df['Name'].tolist()) if 'Name' in df.columns and not df.empty else None
            if st.form_submit_button("❌ Delete Member") and member_to_delete:
                updated_df = df[df['Name'] != member_to_delete].reset_index(drop=True)
                st.session_state[df_key] = updated_df
                save_matrix(team, dept, updated_df)
                st.session_state['flash_msg'] = f"Successfully deleted {member_to_delete}."
                st.rerun()

    with col2:
        st.markdown("#### 🎯 Skills")
        with st.form(f"add_skill_{team}_{dept}", clear_on_submit=True):
            new_skill = st.text_input("Skill Name")
            if st.form_submit_button("➕ Add Skill"):
                if new_skill and new_skill not in df.columns:
                    df[new_skill] = 0
                    st.session_state[df_key] = df
                    save_matrix(team, dept, df)
                    st.session_state['flash_msg'] = f"Successfully added '{new_skill}'!"
                    st.rerun()

        with st.form(f"delete_skill_{team}_{dept}"):
            skills_list = [c for c in df.columns if c not in ['Name', 'Designation']]
            skill_to_delete = st.selectbox("Select Skill to Remove", skills_list) if skills_list else None
            if st.form_submit_button("❌ Delete Skill") and skill_to_delete:
                updated_df = df.drop(columns=[skill_to_delete])
                st.session_state[df_key] = updated_df
                save_matrix(team, dept, updated_df)
                st.session_state['flash_msg'] = f"Successfully removed '{skill_to_delete}'."
                st.rerun()

def render_heatmap(team, dept):
    df = load_matrix(team, dept)
    if df.empty or len(df.columns) <= 2:
        st.info("No skill data available for a dashboard yet.")
        return
        
    heatmap_data = df.drop(columns=['Designation'], errors='ignore')
    skill_cols = [col for col in heatmap_data.columns if col != 'Name']

    def apply_color_logic(val):
        try:
            val = int(float(val)) 
            if val in [0, 1]: return 'background-color: #F8696B; color: black; font-weight: bold;'
            elif val == 2: return 'background-color: #FFEB84; color: black; font-weight: bold;'
            elif val in [3, 4]: return 'background-color: #63BE7B; color: black; font-weight: bold;'
        except: pass
        return ''

    styled_heatmap = heatmap_data.style.map(apply_color_logic, subset=skill_cols)
    st.dataframe(styled_heatmap, use_container_width=True, hide_index=True)

def render_skill_analytics(team, dept):
    disp_name = get_display_name(team, dept)
    st.header(f"📈 {disp_name} Analytics")
    df = load_matrix(team, dept)
    skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]
    
    if not skill_cols or df.empty:
        st.info("No skills available to analyze.")
        return

    numeric_df = df.copy()
    for col in skill_cols:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce').fillna(0).astype(int)
        
    st.subheader("1. Skill-wise People Score")
    selected_skill = st.selectbox("Select a Skill:", skill_cols)
    skill_scores_df = numeric_df[['Name', selected_skill]].sort_values(by=selected_skill, ascending=False)
    
    col1, col2 = st.columns([1, 2])
    with col1: st.dataframe(skill_scores_df, hide_index=True, use_container_width=True)
    with col2: st.bar_chart(skill_scores_df.set_index('Name'), color="#63BE7B")
        
    st.divider()
    st.subheader("2. Top 3 Performers per Skill")
    top3_list = []
    for skill in skill_cols:
        sorted_df = numeric_df[['Name', skill]].sort_values(by=skill, ascending=False)
        sorted_df = sorted_df[sorted_df[skill] > 0] 
        names, scores = sorted_df['Name'].tolist(), sorted_df[skill].tolist()
        top1 = f"{names[0]} ({scores[0]})" if len(names) > 0 else "-"
        top2 = f"{names[1]} ({scores[1]})" if len(names) > 1 else "-"
        top3 = f"{names[2]} ({scores[2]})" if len(names) > 2 else "-"
        top3_list.append({"Skill": skill, "1st Place": top1, "2nd Place": top2, "3rd Place": top3})
    st.dataframe(pd.DataFrame(top3_list), hide_index=True, use_container_width=True)
    
    st.divider()
    st.subheader("3. Zero Skill Details (Score = 0)")
    zero_list = []
    for skill in skill_cols:
        zero_members = numeric_df[numeric_df[skill] == 0]['Name'].tolist()
        if zero_members:
            zero_list.append({"Skill": skill, "Zero Score Count": len(zero_members), "Members with 0 Score": ", ".join(zero_members)})
    
    if zero_list: st.dataframe(pd.DataFrame(zero_list), hide_index=True, use_container_width=True)
    else: st.success("Great job! No one has a zero score in any skill.")


# --- ADMIN & SUPERADMIN ROLE VIEWS ---
role = st.session_state['role']
my_team = st.session_state['team_access']

if role in ['superadmin', 'admin']:
    directory_df = load_directory()
    creds_df = load_credentials()
    
    directory_df['Team'] = directory_df['Team'].astype(str)
    directory_df['Department'] = directory_df['Department'].astype(str)
    creds_df['Team'] = creds_df['Team'].astype(str)
    creds_df['Department'] = creds_df['Department'].astype(str)
    creds_df['Role'] = creds_df['Role'].astype(str)
    
    if role == 'superadmin':
        teams_list = directory_df['Team'].unique().tolist()
    else:
        teams_list = [my_team] if my_team in directory_df['Team'].tolist() else []

    t_edit, t_dash, t_stat, t_hier, t_cred = st.tabs([
        "📝 Matrix Editor", 
        "📊 Rating Dashboard", 
        "📈 Skill Analytics", 
        "🏢 Team Hierarchy", 
        "🔐 Credential Management"
    ])
    
    # --- TAB 1: MATRIX EDITOR ---
    with t_edit:
        st.header("Master Editor")
        colA, colB = st.columns(2)
        
        if teams_list:
            if role == 'superadmin':
                selected_team = colA.selectbox("Select Team:", teams_list)
            else:
                selected_team = my_team
                colA.write(f"**Team:** {selected_team}")
                
            depts_list = directory_df[directory_df['Team'] == selected_team]['Department'].unique().tolist()
            if "None" in depts_list and len(depts_list) == 1:
                selected_dept = "None"
            else:
                selected_dept = colB.selectbox("Select Department:", sorted([d for d in depts_list if d != "None"]))
            
            if selected_team and selected_dept:
                state_key = f"data_{selected_team}_{selected_dept}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = load_matrix(selected_team, selected_dept)
                
                st.divider()
                display_team_matrix(selected_team, selected_dept, state_key)
                display_admin_controls(selected_team, selected_dept, state_key)
        else:
            st.warning("No Teams found. Please create one.")
            
    # --- TAB 2: RATING DASHBOARD ---
    with t_dash:
        st.header("Rating Dashboard")
        st.markdown("🔴 **0-1**: Beginner | 🟡 **2**: Intermediate | 🟢 **3-4**: Proficient/Expert")
        
        if teams_list:
            colA_hm, colB_hm = st.columns(2)
            if role == 'superadmin':
                hm_team = colA_hm.selectbox("Select Team for Dashboard:", teams_list, key="hm_team")
            else:
                hm_team = my_team
                colA_hm.write(f"**Team:** {hm_team}")
                
            hm_depts = directory_df[directory_df['Team'] == hm_team]['Department'].unique().tolist()
            if "None" in hm_depts and len(hm_depts) == 1:
                hm_dept = "None"
            else:
                hm_dept = colB_hm.selectbox("Select Department for Dashboard:", sorted([d for d in hm_depts if d != "None"]), key="hm_dept")
            
            st.divider()
            if hm_team and hm_dept:
                st.subheader(f"{get_display_name(hm_team, hm_dept)} Ratings")
                render_heatmap(hm_team, hm_dept)

    # --- TAB 3: SKILL ANALYTICS ---
    with t_stat:
        if teams_list:
            colA_an, colB_an = st.columns(2)
            if role == 'superadmin':
                an_team = colA_an.selectbox("Select Team for Analytics:", teams_list, key="an_team")
            else:
                an_team = my_team
                colA_an.write(f"**Team:** {an_team}")
                
            an_depts = directory_df[directory_df['Team'] == an_team]['Department'].unique().tolist()
            if "None" in an_depts and len(an_depts) == 1:
                an_dept = "None"
            else:
                an_dept = colB_an.selectbox("Select Department for Analytics:", sorted([d for d in an_depts if d != "None"]), key="an_dept")
            
            st.divider()
            if an_team and an_dept:
                render_skill_analytics(an_team, an_dept)

    # --- TAB 4: TEAM HIERARCHY ---
    with t_hier:
        st.header("🏢 Team Hierarchy Setup")
        if role == 'superadmin':
            st.write("Manage your organizational structure below.")
            
            action_type = st.radio("What would you like to do?", ["Create a New Team", "Add Department to Existing Team"])
            
            with st.form("new_hierarchy_form", clear_on_submit=True):
                if action_type == "Create a New Team":
                    has_dept = st.radio("Does this new team have departments?", ["No, just a Team", "Yes, Team with Departments"])
                    new_t_name = st.text_input("New Team Name (e.g., 'Apollo')")
                    new_d_name = st.text_input("Department Name (e.g., 'Backend')") if has_dept == "Yes, Team with Departments" else "None"
                else:
                    if teams_list:
                        new_t_name = st.selectbox("Select Existing Team", teams_list)
                        new_d_name = st.text_input("New Department Name (e.g., 'QA')")
                    else:
                        st.warning("No teams exist yet. Please create a new team first.")
                        new_t_name, new_d_name = None, None
                
                if st.form_submit_button("Create Structure"):
                    if new_t_name and new_d_name:
                        if new_d_name == "None" and action_type == "Add Department to Existing Team":
                             st.error("Please provide a valid department name.")
                        else:
                            add_to_directory(new_t_name, new_d_name)
                            msg = f"Created Team '{new_t_name}'" if new_d_name == "None" else f"Added '{new_d_name}' to '{new_t_name}'"
                            st.session_state['flash_msg'] = msg
                            st.rerun()
            
            st.divider()
            st.subheader("🗑️ Delete Structure")
            col_del1, col_del2 = st.columns(2)
            del_team = col_del1.selectbox("Select Team to Delete", teams_list, key="del_team")
            
            if del_team:
                del_depts = directory_df[directory_df['Team'] == del_team]['Department'].tolist()
                del_dept = col_del2.selectbox("Select Department to Delete", sorted(del_depts), key="del_dept")
                
                if st.button("❌ Delete Selection", type="secondary"):
                    delete_from_directory(del_team, del_dept)
                    st.session_state['flash_msg'] = f"Removed {del_team} - {del_dept} from the directory."
                    st.rerun()

            st.divider()
            st.subheader("Current Master Directory")
            st.dataframe(directory_df, hide_index=True, use_container_width=True)
            
        else:
            st.warning("Access Restricted: Only Superadmins can manage the global team hierarchy.")
            st.write("Your current active departments:")
            my_depts = directory_df[directory_df['Team'] == my_team]
            st.dataframe(my_depts, hide_index=True)

    # --- TAB 5: CREDENTIAL MANAGEMENT (COMBINED) ---
    with t_cred:
        st.header("Setup New User Credential")
        
        show_form = True 
        c_team, c_dept = None, None
        
        if role == 'superadmin':
            c_role = st.selectbox("Assign Role", ["editor", "admin", "superadmin"])
            
            if c_role == "editor":
                existing_editors = creds_df[creds_df['Role'] == 'editor']
                existing_combos = set(zip(existing_editors['Team'], existing_editors['Department']))
                all_combos = set(zip(directory_df['Team'], directory_df['Department']))
                available_combos = all_combos - existing_combos
                
                if not available_combos:
                    st.warning("All Team & Department combinations already have editor credentials assigned.")
                    show_form = False
                else:
                    available_teams = sorted(list(set([t for t, d in available_combos])))
                    c_team = st.selectbox("Assign Team", available_teams, key="new_cred_team")
                    available_depts = sorted([d for t, d in available_combos if t == c_team])
                    
                    if "None" in available_depts and len(available_depts) == 1:
                        c_dept = "None"
                        st.info("This team has no departments. Creating a Team-wide Editor login.")
                    else:
                        c_dept = st.selectbox("Assign Department", available_depts)
                        
            elif c_role == "admin":
                existing_admins = creds_df[creds_df['Role'] == 'admin']['Team'].tolist()
                available_teams = sorted([t for t in teams_list if t not in existing_admins])
                
                if not available_teams:
                    st.warning("All Teams already have an admin credential assigned.")
                    show_form = False
                else:
                    c_team = st.selectbox("Assign Team Admin rights to:", available_teams, key="new_cred_team")
                    c_dept = "All"
                    st.info(f"This user will manage all departments inside '{c_team}'.")
            else:
                c_team, c_dept = "All", "All"
                st.info("Superadmins have full access across the entire organization.")
                
        else: # Team Admin Logic
            c_role = "editor"
            st.info("As a Team Admin, you can only create 'Editor' accounts for your own team.")
            c_team = my_team
            existing_editors = creds_df[(creds_df['Role'] == 'editor') & (creds_df['Team'] == my_team)]['Department'].tolist()
            all_depts = directory_df[directory_df['Team'] == my_team]['Department'].tolist()
            available_depts = sorted([d for d in all_depts if d not in existing_editors])
            
            if not available_depts:
                st.warning(f"All departments in {my_team} already have editor credentials assigned.")
                show_form = False
            else:
                if "None" in available_depts and len(available_depts) == 1:
                    c_dept = "None"
                else:
                    c_dept = st.selectbox("Assign Department", available_depts)

        if show_form:
            with st.form("new_user_form", clear_on_submit=True):
                c_user = st.text_input("New Username")
                c_pass = st.text_input("New Password", type="password")
                submitted = st.form_submit_button("Create Credential")
                
                if submitted:
                    if c_team is None:
                        st.error("No valid team/department available to assign.")
                    elif c_user and c_pass:
                        success = add_credential(c_user, c_pass, c_role, c_team, c_dept)
                        if success:
                            st.session_state['flash_msg'] = f"Successfully created {c_role} user '{c_user}'!"
                            st.rerun()
                        else:
                            st.error("Username already exists!")

        st.divider()
        st.header("Credential List")
        st.write("View, edit, or delete existing user credentials directly in the table below.")
        
        if role == 'superadmin':
            view_df = creds_df.copy()
            role_options = ["editor", "admin", "superadmin"]
        else:
            view_df = creds_df[creds_df['Team'] == my_team].copy()
            role_options = ["editor"]
            
        col_config = {
            "Username": st.column_config.TextColumn("Username", required=True),
            "Password": st.column_config.TextColumn("Password (Visible)", required=True),
            "Role": st.column_config.SelectboxColumn("Role", options=role_options, required=True),
            "Department": st.column_config.TextColumn("Department", required=True)
        }
        
        if role != 'superadmin':
            col_config["Team"] = st.column_config.TextColumn("Team", disabled=True)
            
        edited_creds = st.data_editor(
            view_df,
            column_config=col_config,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key="role_mgmt_editor"
        )
        
        if st.button("💾 Save Credential Changes", type="primary"):
            if 'superadmin' not in edited_creds['Username'].values and role == 'superadmin':
                st.error("Error: You cannot delete the master 'superadmin' account!")
            else:
                if role == 'superadmin':
                    new_creds = edited_creds
                else:
                    edited_creds['Team'] = my_team 
                    other_teams_df = creds_df[creds_df['Team'] != my_team]
                    new_creds = pd.concat([other_teams_df, edited_creds], ignore_index=True)
                    
                conn.update(worksheet="Credentials", data=new_creds)
                st.session_state['flash_msg'] = "User credentials updated successfully!"
                st.rerun()

# --- EDITOR ROLE VIEW ---
else:
    my_dept = st.session_state['dept_access']
    
    st.info(f"You are editing the {get_display_name(my_team, my_dept)} Skill Matrix.")
    
    state_key = f"data_{my_team}_{my_dept}"
    if state_key not in st.session_state:
        st.session_state[state_key] = load_matrix(my_team, my_dept)
        
    display_team_matrix(my_team, my_dept, state_key)
