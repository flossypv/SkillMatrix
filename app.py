import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials
import time

# 1. Page Configuration
st.set_page_config(page_title="SkillMatrix", layout="wide", initial_sidebar_state="expanded")

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
    if username in creds_df['Username'].values: return False
    new_user = pd.DataFrame([{"Username": username, "Password": password, "Role": role, "Team": team, "Department": dept}])
    updated_creds = pd.concat([creds_df, new_user], ignore_index=True)
    conn.update(worksheet="Credentials", data=updated_creds)
    return True

def delete_credential(username):
    creds_df = load_credentials()
    updated_creds = creds_df[creds_df['Username'] != username]
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

def get_sheet_name(team, dept): return f"{team}_{dept}"
def get_display_name(team, dept): return f"{team} - {dept}"

def load_matrix(team, dept):
    sheet_name = get_sheet_name(team, dept)
    try:
        df = conn.read(worksheet=sheet_name, ttl=0).dropna(how='all', axis=1).dropna(how='all', axis=0)
        if df.empty: raise Exception("Empty Matrix")
    except Exception:
        if team == "Canyon" and dept == "QA": df = pd.DataFrame(default_qa)
        elif team == "Canyon" and dept == "UIUX": df = pd.DataFrame(default_uiux)
        elif team == "Canyon" and dept == "Dev": df = pd.DataFrame(default_dev)
        else: df = pd.DataFrame(columns=['Name', 'Designation'])
        ensure_worksheet_exists(sheet_name)
        conn.update(worksheet=sheet_name, data=df)
        
    for col in df.columns:
        if col not in ['Name', 'Designation']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df

def save_matrix(team, dept, df):
    conn.update(worksheet=get_sheet_name(team, dept), data=df)

def add_to_directory(team, dept):
    dir_df = load_directory()
    if not ((dir_df['Team'] == team) & (dir_df['Department'] == dept)).any():
        new_row = pd.DataFrame([{"Team": team, "Department": dept}])
        conn.update(worksheet="Directory", data=pd.concat([dir_df, new_row], ignore_index=True))
        sheet_name = get_sheet_name(team, dept)
        ensure_worksheet_exists(sheet_name)
        conn.update(worksheet=sheet_name, data=pd.DataFrame(columns=['Name', 'Designation']))

def delete_from_directory(team, dept):
    dir_df = load_directory()
    updated_dir = dir_df[~((dir_df['Team'] == team) & (dir_df['Department'] == dept))]
    conn.update(worksheet="Directory", data=updated_dir)

# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['team_access'] = None
    st.session_state['dept_access'] = None

# --- AUTHENTICATED OR LOGIN LOGIC ---
if not st.session_state['authenticated']:
    # ==========================================
    # --- BEAUTIFUL LOGIN & INTRO PAGE ---
    # ==========================================
    
    # Header Section
    st.markdown("<h1 style='text-align: center; color: #2e66ff;'>SkillMatrix</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #5c7cfa;'>Empower your Organization's Potential</h3>", unsafe_allow_html=True)
    
    col_intro, col_divider, col_login = st.columns([1.5, 0.1, 1.2])

    with col_intro:
        st.markdown("<br>", unsafe_allow_html=True)
        intro_icon, intro_title = st.columns([1, 10])
        with intro_icon: st.markdown("### 🚀")
        with intro_title: st.markdown("### Welcome to SkillMatrix")
        
        st.markdown("""
        Unlock a modern view of your organization's human capital. SkillMatrix visualizes 
        expertise across teams and departments, enabling you to build stronger, more agile organizations.
        
        **Key Capabilities:**
        """)
        
        feat1, feat2 = st.columns(2)
        with feat1:
            st.markdown("""
            📊 **Real-time Heatmaps**
            > Instantly spot skill gaps and core strengths across teams.
            """)
        with feat2:
            st.markdown("""
            🏢 **Agile Org Hierarchies**
            > View and manage structures with simple hierarchy controls.
            """)

        feat3, feat4 = st.columns(2)
        with feat3:
            st.markdown("""
            📈 **Targeted Analytics**
            > Identify top talent and focused training opportunities.
            """)
        with feat4:
            st.markdown("""
            🔐 **Fine-grained Security**
            > Role-based access for Admins, Managers, and Editors.
            """)
            
        st.divider()
        st.info("**Already a client?** Use your corporate credentials to access your organization's SkillMatrix.")

    with col_divider:
        st.markdown(
            """
            <div style="border-left: 2px solid rgba(128, 128, 128, 0.2); min-height: 500px; height: 100%; margin: 0 auto;"></div>
            """,
            unsafe_allow_html=True
        )

    with col_login:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True) # Better vertical alignment
        form_icon, form_title = st.columns([1, 10])
        with form_icon: st.markdown("### 🔐")
        with form_title: st.markdown("### Account Login")
        
        st.markdown("Welcome! Log in below to access your organization's SkillMatrix dashboard.")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g., dominicraj")
            password = st.text_input("Password", type="password", placeholder="Corporate Password")
            submit = st.form_submit_button("Log In", use_container_width=True, type="primary")

            if submit:
                creds_df = load_credentials()
                user_row = creds_df[creds_df['Username'] == username]
                if not user_row.empty and str(user_row.iloc[0]['Password']) == password:
                    st.session_state['authenticated'] = True
                    st.session_state['role'] = str(user_row.iloc[0]['Role'])
                    st.session_state['username'] = username
                    st.session_state['team_access'] = str(user_row.iloc[0]['Team'])
                    st.session_state['dept_access'] = str(user_row.iloc[0]['Department'])
                    st.rerun()
                else:
                    st.error("Invalid corporate credentials.")
        
        st.divider()
        st.caption("**Edge Client Support:** If you have trouble logging in, please contact your organization's SkillMatrix administrator.")
    
    st.stop()

# --- SIDEBAR: CLEAN USER PROFILE & MENU ---
role = st.session_state['role']
my_team = st.session_state['team_access']
my_dept = st.session_state['dept_access']

# Profile Card
st.sidebar.markdown("### SkillMatrix Profile")
prof_icon, prof_details = st.columns([1, 4])
with prof_icon: st.markdown("### 👤")
with prof_details:
    st.markdown(f"**Username:** {st.session_state['username']}")
    st.markdown(f"**Role:** {role.capitalize()}")
    if role != 'superadmin':
        team_display = f"**Team:** {my_team}"
        if my_dept and my_dept != "None": team_display += f" | {my_dept}"
        st.caption(team_display)

if st.sidebar.button("Logout", use_container_width=True, type="secondary"):
    for key in ['authenticated', 'role', 'username', 'team_access', 'dept_access']: st.session_state[key] = None
    st.rerun()
st.sidebar.divider()

# Main Header
if role == 'superadmin':
    st.title("🌐 Enterprise SkillMatrix")
else:
    st.title(f"🏢 {my_team} SkillMatrix")
st.divider()

if 'flash_msg' in st.session_state:
    st.success(st.session_state['flash_msg'])
    del st.session_state['flash_msg']
if 'flash_error' in st.session_state:
    st.error(st.session_state['flash_error'])
    del st.session_state['flash_error']

# --- HELPER: RENDER TEAM SELECTOR ---
def render_team_selector(role, my_team, teams_list, directory_df):
    if role == 'superadmin':
        selected_team = st.selectbox("Select Team:", teams_list)
    else:
        selected_team = my_team
        st.caption(f"**Team:** {selected_team}")
        
    depts = directory_df[directory_df['Team'] == selected_team]['Department'].unique().tolist()
    if not depts: depts = ["Default"]
    selected_dept = st.selectbox("Select Department:", depts)
    return selected_team, selected_dept

# --- ADMIN VIEW ---
if role in ['superadmin', 'admin']:
    directory_df = load_directory()
    teams_list = directory_df['Team'].unique().tolist()
    if role == 'admin' and my_team not in teams_list: teams_list.append(my_team)

    admin_nav = st.sidebar.radio("Organization View", ["📊 Dashboard", "📈 Skill Analytics", "📝 Matrix Editor", "👤 Team Members", "🎯 Skills", "🏢 Hierarchy", "🔐 Credentials"])

    # --- TAB 1: DASHBOARD ---
    if admin_nav == "📊 Dashboard":
        st.header("Rating Dashboard")
        
        key_pop = st.popover("🟢 Rating Key (Red-Amber-Green)")
        with key_pop:
            st.markdown("""
            * 🔴 **0-1**: Beginner (Needs training)
            * 🟡 **2**: Intermediate (Working knowledge)
            * 🟢 **3-4**: Proficient/Expert (Role model)
            """)

        sel_team, sel_dept = render_team_selector(role, my_team, teams_list, directory_df)
        df = load_matrix(sel_team, sel_dept)
        
        skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]
        if not skill_cols or df.empty:
            st.info("No skill data available. Please check members and skills.")
        else:
            heatmap_data = df.drop(columns=['Designation'])
            sk_cols = heatmap_data.columns.tolist()[1:]
            
            def apply_style(val):
                color = ''
                if val <= 1: color = '#F8696B'  # Light red
                elif val == 2: color = '#FFEB84' # Light yellow
                elif val >= 3: color = '#63BE7B' # Light green
                return f'background-color: {color}; color: black; font-weight: bold;'
            
            st.dataframe(heatmap_data.style.applymap(apply_style, subset=sk_cols), use_container_width=True, hide_index=True)

    # --- TAB 2: ANALYTICS ---
    elif admin_nav == "📈 Skill Analytics":
        st.header("Skill Analytics")
        sel_team, sel_dept = render_team_selector(role, my_team, teams_list, directory_df)
        df = load_matrix(sel_team, sel_dept)
        
        skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]
        
        if not skill_cols or df.empty:
            st.info("No skill data to analyze.")
        else:
            # Reformat to handle numbers
            for col in skill_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

            st.subheader("1. Skill-wise Proficiency (Scores 0-4)")
            selected_skill = st.selectbox("Select a Skill to Analyze:", skill_cols)
            skill_scores = df[['Name', selected_skill]].sort_values(by=selected_skill, ascending=False)
            
            c_grid, c_chart = st.columns([1, 2])
            with c_grid: st.dataframe(skill_scores, hide_index=True)
            with c_chart: st.bar_chart(skill_scores.set_index('Name'))
            
            st.divider()
            st.subheader("2. Top Performers by Skill (Scores > 0)")
            top3 = []
            for skill in skill_cols:
                sorted_d = df[['Name', skill]].sort_values(by=skill, ascending=False)
                sorted_d = sorted_d[sorted_d[skill] > 0] # only positive scores
                names, scores = sorted_d['Name'].tolist(), sorted_d[skill].tolist()
                
                top3.append({
                    "Skill": skill, 
                    "1st": f"{names[0]} ({scores[0]})" if len(names) > 0 else "-", 
                    "2nd": f"{names[1]} ({scores[1]})" if len(names) > 1 else "-", 
                    "3rd": f"{names[2]} ({scores[2]})" if len(names) > 2 else "-"
                })
            
            st.dataframe(pd.DataFrame(top3), hide_index=True, use_container_width=True)

    # --- TAB 3: MATRIX EDITOR ---
    elif admin_nav == "📝 Matrix Editor":
        st.header("Matrix Editor")
        sel_team, sel_dept = render_team_selector(role, my_team, teams_list, directory_df)
        state_key = f"data_{sel_team}_{sel_dept}"
        
        if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_team, sel_dept)
        df = st.session_state[state_key]
        
        skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]
        col_config = {col: st.column_config.SelectboxColumn(col, options=[0, 1, 2, 3, 4], required=True) for col in skill_cols}

        edited_df = st.data_editor(df, column_config=col_config, hide_index=True, use_container_width=True, key=f"editor_{sel_team}_{sel_dept}")

        if st.button("Save Database", type="primary"):
            # Ensure numbers
            for col in skill_cols:
                edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0).astype(int)
            st.session_state[state_key] = edited_df
            save_matrix(sel_team, sel_dept, edited_df)
            st.success("Database saved successfully!")
            time.sleep(1)
            st.rerun()

    # --- TAB 4: MEMBERS ---
    elif admin_nav == "👤 Team Members":
        st.header("Manage Members")
        sel_team, sel_dept = render_team_selector(role, my_team, teams_list, directory_df)
        state_key = f"data_{sel_team}_{sel_dept}"
        if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_team, sel_dept)
        df = st.session_state[state_key]
        
        c_mem_grid, c_mem_form = st.columns([1, 1])
        with c_mem_grid:
            st.subheader("Current Members")
            st.dataframe(df[['Name', 'Designation']], hide_index=True, use_container_width=True)

        with c_mem_form:
            add_exp = st.expander("➕ Add Member", expanded=True)
            with add_exp:
                with st.form(f"add_member_{sel_team}_{sel_dept}"):
                    new_name = st.text_input("Full Name")
                    new_desig = st.text_input("Designation")
                    add_submit = st.form_submit_button("Add Member")
                    
                    if add_submit and new_name:
                        new_row = {'Name': new_name, 'Designation': new_desig}
                        for skill in df.columns:
                            if skill not in ['Name', 'Designation']: new_row[skill] = 0
                        
                        updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        st.session_state[state_key] = updated_df
                        save_matrix(sel_team, sel_dept, updated_df)
                        st.session_state['flash_msg'] = f"Member '{new_name}' added."
                        st.rerun()

            rem_exp = st.expander("❌ Remove Member")
            with rem_exp:
                with st.form(f"remove_member_{sel_team}_{sel_dept}"):
                    mem_to_rem = st.selectbox("Select Member to Remove:", df['Name'].tolist())
                    rem_submit = st.form_submit_button("Remove Member", type="secondary")
                    
                    if rem_submit:
                        updated_df = df[df['Name'] != mem_to_rem]
                        st.session_state[state_key] = updated_df
                        save_matrix(sel_team, sel_dept, updated_df)
                        st.session_state['flash_msg'] = f"Member '{mem_to_rem}' removed."
                        st.rerun()

    # --- TAB 5: SKILLS ---
    elif admin_nav == "🎯 Skills":
        st.header("Manage Skills")
        sel_team, sel_dept = render_team_selector(role, my_team, teams_list, directory_df)
        state_key = f"data_{sel_team}_{sel_dept}"
        if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_team, sel_dept)
        df = st.session_state[state_key]
        
        current_skills = [col for col in df.columns if col not in ['Name', 'Designation']]
        c_sk_grid, c_sk_form = st.columns([1, 1])
        with c_sk_grid:
            st.subheader("Current Skills")
            st.dataframe(pd.DataFrame({"Skill Name": current_skills}), hide_index=True, use_container_width=True)

        with c_sk_form:
            add_sk_exp = st.expander("➕ Add Skill", expanded=True)
            with add_sk_exp:
                with st.form(f"add_skill_{sel_team}_{sel_dept}"):
                    new_skill = st.text_input("New Skill Name")
                    add_sk_submit = st.form_submit_button("Add Skill")
                    
                    if add_sk_submit and new_skill:
                        if new_skill not in df.columns:
                            df[new_skill] = 0
                            st.session_state[state_key] = df
                            save_matrix(sel_team, sel_dept, df)
                            st.session_state['flash_msg'] = f"Skill '{new_skill}' added."
                            st.rerun()
                        else: st.error("Skill already exists.")

            rem_sk_exp = st.expander("❌ Remove Skill")
            with rem_sk_exp:
                with st.form(f"remove_skill_{sel_team}_{sel_dept}"):
                    sk_to_rem = st.selectbox("Select Skill to Remove:", current_skills)
                    rem_sk_submit = st.form_submit_button("Remove Skill", type="secondary")
                    
                    if rem_sk_submit:
                        updated_df = df.drop(columns=[sk_to_rem])
                        st.session_state[state_key] = updated_df
                        save_matrix(sel_team, sel_dept, updated_df)
                        st.session_state['flash_msg'] = f"Skill '{sk_to_rem}' removed."
                        st.rerun()

    # --- TAB 6: HIERARCHY ---
    elif admin_nav == "🏢 Hierarchy":
        st.header("Hierarchy Setup")
        if role == 'superadmin':
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Agile Organization Structure")
                st.dataframe(directory_df, hide_index=True, use_container_width=True)

            with col2:
                with st.form("add_hierarchy"):
                    new_team = st.text_input("New Team Name")
                    new_dept = st.text_input("New Department Name")
                    add_submit = st.form_submit_button("Create Structure")
                    if add_submit and new_team and new_dept:
                        add_to_directory(new_team, new_dept)
                        st.success(f"Structure '{new_team}/{new_dept}' created.")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("Your team structure is predefined. If changes are needed, please contact Superadmin.")
            st.dataframe(directory_df[directory_df['Team'] == my_team], hide_index=True, use_container_width=True)

    # --- TAB 7: CREDENTIALS ---
    elif admin_nav == "🔐 Credentials":
        if role == 'superadmin':
            st.header("Creds Manager")
            creds_df = load_credentials()
            st.dataframe(creds_df[['Username', 'Role', 'Team', 'Department']], hide_index=True, use_container_width=True)
            
            with st.expander("➕ Create New Credential"):
                with st.form("add_credential_form"):
                    c_user = st.text_input("Username")
                    c_pass = st.text_input("Password", type="password")
                    c_role = st.selectbox("Role", ["admin", "editor"])
                    
                    # Set access scope
                    if c_role == "admin":
                        c_team = st.selectbox("Team Scope:", teams_list)
                        c_dept = "All"
                    else: # editor
                        avail_scopes = []
                        for team in teams_list:
                            depts = directory_df[directory_df['Team'] == team]['Department'].unique().tolist()
                            for d in depts: avail_scopes.append(f"{team} - {d}")
                        
                        selected_scope = st.selectbox("Specific Scope:", avail_scopes)
                        c_team, c_dept = selected_scope.split(" - ")

                    c_submit = st.form_submit_button("Add Credential")
                    if c_submit and c_user and c_pass:
                        if add_credential(c_user, c_pass, c_role, c_team, c_dept):
                            st.success(f"Credential '{c_user}' created.")
                            time.sleep(1)
                            st.rerun()
                        else: st.error("Username already exists.")

            with st.expander("❌ Remove Credential"):
                with st.form("remove_credential_form"):
                    c_rem_user = st.selectbox("Username", creds_df[creds_df['Username'] != 'superadmin']['Username'].tolist())
                    c_rem_submit = st.form_submit_button("Remove Credential", type="secondary")
                    if c_rem_submit:
                        delete_credential(c_rem_user)
                        st.success(f"Credential '{c_rem_user}' removed.")
                        time.sleep(1)
                        st.rerun()
        else: st.info("Only Superadmin can manage credentials.")

# --- EDITOR VIEW ---
else:
    state_key = f"data_{my_team}_{my_dept}"
    if state_key not in st.session_state: st.session_state[state_key] = load_matrix(my_team, my_dept)
    df = st.session_state[state_key]
    
    st.markdown(f"**Welcome to corporate SkillMatrix.**")
    st.markdown(f"You are currently contributing to the {get_display_name(my_team, my_dept)} Skill Matrix.")
    
    skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]
    col_config = {col: st.column_config.SelectboxColumn(col, options=[0, 1, 2, 3, 4], required=True) for col in skill_cols}

    edited_df = st.data_editor(df, column_config=col_config, hide_index=True, use_container_width=True, key=f"editor_{my_team}_{my_dept}")

    if st.button("Save Changes", type="primary"):
        # Ensure numbers
        for col in skill_cols:
            edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0).astype(int)
        st.session_state[state_key] = edited_df
        save_matrix(my_team, my_dept, edited_df)
        st.success("Changes saved successfully!")
        time.sleep(1)
        st.rerun()
