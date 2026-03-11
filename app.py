import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials
import time  # Imported to handle Google API sync delays

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
    if username in creds_df['Username'].astype(str).values: return False
    new_user = pd.DataFrame([{"Username": username, "Password": password, "Role": role, "Team": team, "Department": dept}])
    updated_creds = pd.concat([creds_df, new_user], ignore_index=True)
    conn.update(worksheet="Credentials", data=updated_creds)
    st.cache_data.clear() # Clear cache to ensure immediate read
    return True

def delete_credential(username):
    creds_df = load_credentials()
    updated_creds = creds_df[creds_df['Username'].astype(str) != str(username)]
    conn.update(worksheet="Credentials", data=updated_creds)
    st.cache_data.clear()

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

def get_sheet_name(team, dept): return str(team) if str(dept) == "None" else f"{team}_{dept}"
def get_display_name(team, dept): return str(team) if str(dept) == "None" else f"{team} - {dept}"

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
    conn.update(worksheet=get_sheet_name(team, dept), data=df)
    st.cache_data.clear()

def add_to_directory(team, dept):
    dir_df = load_directory()
    if not ((dir_df['Team'].astype(str).str.strip() == str(team).strip()) & (dir_df['Department'].astype(str).str.strip() == str(dept).strip())).any():
        new_row = pd.DataFrame([{"Team": str(team).strip(), "Department": str(dept).strip()}])
        conn.update(worksheet="Directory", data=pd.concat([dir_df, new_row], ignore_index=True))
        
        sheet_name = get_sheet_name(team, dept)
        ensure_worksheet_exists(sheet_name)
        conn.update(worksheet=sheet_name, data=pd.DataFrame(columns=['Name', 'Designation']))
        st.cache_data.clear() # Fixes the "two-click" refresh bug

def delete_from_directory(team, dept):
    dir_df = load_directory()
    updated_dir = dir_df[~((dir_df['Team'].astype(str).str.strip() == str(team).strip()) & (dir_df['Department'].astype(str).str.strip() == str(dept).strip()))]
    conn.update(worksheet="Directory", data=updated_dir)
    st.cache_data.clear()

# --- AUTHENTICATION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.session_state['team_access'] = None
    st.session_state['dept_access'] = None

# --- BEAUTIFUL LOGIN PAGE ---
if not st.session_state['authenticated']:
    col_info, col_divider, col_login = st.columns([1.3, 0.1, 0.9])
    
    with col_info:
        st.markdown("# 🚀 SkillMatrix")
        st.markdown("### Empowering Teams Through Skill Tracking")
        st.write("Track, analyze, and manage your organization's capabilities securely with our dynamic dashboard.")
        st.markdown("---")
        info1, info2 = st.columns(2)
        with info1:
            st.info("**📊 Interactive Heatmaps**\n\nInstantly spot skill gaps and strengths across your entire workforce.")
            st.warning("**🏢 Custom Hierarchies**\n\nTailor the database exactly to your organizational structure.")
        with info2:
            st.success("**📈 Deep Analytics**\n\nIdentify top performers and targeted training opportunities.")
            st.error("**🔐 Role-Based Access**\n\nSecure, specific views for Admins, Managers, and Editors.")
            
    with col_divider:
        st.markdown(
            """
            <div style="border-left: 2px solid rgba(128, 128, 128, 0.2); min-height: 550px; height: 100%; margin: 0 auto;"></div>
            """,
            unsafe_allow_html=True
        )

    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        st.subheader("🔐 Secure Login")
        st.write("Please log in to access your dashboard.")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
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
                    if "admin_nav" in st.session_state:
                        del st.session_state["admin_nav"]
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    st.stop()


# --- MAIN APP ROUTING ---
st.sidebar.title("Profile")
st.sidebar.write(f"**User:** {st.session_state['username']}")
if st.session_state['role'] == 'superadmin': st.sidebar.write("**Access:** Superadmin")
elif st.session_state['role'] == 'admin': st.sidebar.write(f"**Access:** Team Admin ({st.session_state['team_access']})")
else:
    st.sidebar.write(f"**Team:** {st.session_state['team_access']}")
    if st.session_state['dept_access'] != "None": st.sidebar.write(f"**Department:** {st.session_state['dept_access']}")

if st.sidebar.button("Logout"):
    for key in ['authenticated', 'role', 'username', 'team_access', 'dept_access']: st.session_state[key] = None
    if "admin_nav" in st.session_state: del st.session_state["admin_nav"]
    st.rerun()

# DYNAMIC HEADER
st.title("🌐 Enterprise SkillMatrix" if st.session_state['role'] == 'superadmin' else f"🏢 {st.session_state['team_access']} SkillMatrix")

if 'flash_msg' in st.session_state:
    st.success(st.session_state['flash_msg'])
    del st.session_state['flash_msg']
if 'flash_error' in st.session_state:
    st.error(st.session_state['flash_error'])
    del st.session_state['flash_error']


# --- REUSABLE UI HELPERS ---
def render_team_selector(prefix, role, my_team, teams_list, directory_df):
    colA, colB = st.columns(2)
    if role == 'superadmin':
        selected_team = colA.selectbox("Select Team:", teams_list, key=f"{prefix}_t")
    else:
        selected_team = my_team
        colA.write(f"**Team:** {selected_team}")
        
    if not selected_team: return None, None
    
    depts = directory_df[directory_df['Team'] == selected_team]['Department'].unique().tolist()
    if "None" in depts and len(depts) == 1:
        return selected_team, "None"
    else:
        selected_dept = colB.selectbox("Select Department:", sorted([d for d in depts if d != "None"]), key=f"{prefix}_d")
        return selected_team, selected_dept


# --- ADMIN & SUPERADMIN ROLE VIEWS ---
role = st.session_state['role']
my_team = st.session_state['team_access']

if role in ['superadmin', 'admin']:
    directory_df = load_directory()
    creds_df = load_credentials()
    
    directory_df['Team'], directory_df['Department'] = directory_df['Team'].astype(str), directory_df['Department'].astype(str)
    creds_df['Team'], creds_df['Department'], creds_df['Role'] = creds_df['Team'].astype(str), creds_df['Department'].astype(str), creds_df['Role'].astype(str)
    
    teams_list = directory_df['Team'].unique().tolist() if role == 'superadmin' else [my_team] if my_team in directory_df['Team'].tolist() else []

    # --- TOP LEVEL NAVIGATION ROUTER ---
    if role == 'superadmin':
        nav_options = [
            "📝 Matrix Editor", "👤 Members", "🎯 Skills", 
            "📊 Dashboard", "📈 Analytics", "🏢 Hierarchy", "🔐 Credentials"
        ]
    else:
        nav_options = ["📝 Matrix Editor", "👤 Members", "🎯 Skills"]
        
    if st.session_state.get("admin_nav") not in nav_options:
        st.session_state["admin_nav"] = nav_options[0]

    selected_tab = st.radio("Menu Navigation", nav_options, horizontal=True, label_visibility="collapsed", key="admin_nav")
    st.divider()
    
    # --- TAB 1: MATRIX EDITOR ---
    if selected_tab == "📝 Matrix Editor":
        st.header("Matrix Editor")
        if teams_list:
            sel_t, sel_d = render_team_selector("edit", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                state_key = f"data_{sel_t}_{sel_d}"
                if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_t, sel_d)
                
                df = st.session_state[state_key]
                skill_cols = [c for c in df.columns if c not in ['Name', 'Designation']]
                col_config = {c: st.column_config.SelectboxColumn(c, options=[0, 1, 2, 3, 4], required=True) for c in skill_cols}

                edited_df = st.data_editor(df, column_config=col_config, hide_index=True, use_container_width=True, key=f"editor_{sel_t}_{sel_d}", num_rows="fixed")
                if st.button("💾 Save Scores", type="primary"):
                    edited_df.fillna(0, inplace=True) 
                    for c in skill_cols: edited_df[c] = pd.to_numeric(edited_df[c], errors='coerce').fillna(0).astype(int)
                    st.session_state[state_key] = edited_df
                    save_matrix(sel_t, sel_d, edited_df)
                    st.session_state['flash_msg'] = "Scores saved successfully!"
                    time.sleep(1) # Allow Google API to sync
                    st.rerun()
        else: st.warning("No Teams found. Please create one.")
            
    # --- TAB 2: MEMBERS ---
    elif selected_tab == "👤 Members":
        st.header("Manage Members")
        if teams_list:
            sel_t, sel_d = render_team_selector("mem", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                state_key = f"data_{sel_t}_{sel_d}"
                if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_t, sel_d)
                df = st.session_state[state_key]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### ➕ Add Member")
                    with st.form(f"add_mem_{sel_t}_{sel_d}", clear_on_submit=True):
                        new_name = st.text_input("Name")
                        new_desig = st.text_input("Designation")
                        if st.form_submit_button("Add Member") and new_name:
                            new_row = {'Name': new_name, 'Designation': new_desig}
                            for c in df.columns: 
                                if c not in ['Name', 'Designation']: new_row[c] = 0
                            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                            st.session_state[state_key] = updated_df
                            save_matrix(sel_t, sel_d, updated_df)
                            st.session_state['flash_msg'] = f"Added {new_name}!"
                            time.sleep(1)
                            st.rerun()
                with col2:
                    st.markdown("#### ❌ Remove Member")
                    with st.form(f"del_mem_{sel_t}_{sel_d}"):
                        mem_to_del = st.selectbox("Select Member", df['Name'].tolist()) if 'Name' in df.columns and not df.empty else None
                        if st.form_submit_button("Delete Member") and mem_to_del:
                            updated_df = df[df['Name'] != mem_to_del].reset_index(drop=True)
                            st.session_state[state_key] = updated_df
                            save_matrix(sel_t, sel_d, updated_df)
                            st.session_state['flash_msg'] = f"Deleted {mem_to_del}."
                            time.sleep(1)
                            st.rerun()

    # --- TAB 3: SKILLS ---
    elif selected_tab == "🎯 Skills":
        st.header("Manage Skills")
        if teams_list:
            sel_t, sel_d = render_team_selector("skil", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                state_key = f"data_{sel_t}_{sel_d}"
                if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_t, sel_d)
                df = st.session_state[state_key]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### ➕ Add Skill")
                    with st.form(f"add_skil_{sel_t}_{sel_d}", clear_on_submit=True):
                        new_skill = st.text_input("Skill Name")
                        if st.form_submit_button("Add Skill") and new_skill:
                            if new_skill not in df.columns:
                                df[new_skill] = 0
                                st.session_state[state_key] = df
                                save_matrix(sel_t, sel_d, df)
                                st.session_state['flash_msg'] = f"Added '{new_skill}'!"
                                time.sleep(1)
                                st.rerun()
                with col2:
                    st.markdown("#### ❌ Remove Skill")
                    with st.form(f"del_skil_{sel_t}_{sel_d}"):
                        skil_list = [c for c in df.columns if c not in ['Name', 'Designation']]
                        skil_to_del = st.selectbox("Select Skill", skil_list) if skil_list else None
                        if st.form_submit_button("Delete Skill") and skil_to_del:
                            updated_df = df.drop(columns=[skil_to_del])
                            st.session_state[state_key] = updated_df
                            save_matrix(sel_t, sel_d, updated_df)
                            st.session_state['flash_msg'] = f"Removed '{skil_to_del}'."
                            time.sleep(1)
                            st.rerun()

    # --- TAB 4: RATING DASHBOARD (SUPERADMIN ONLY) ---
    elif selected_tab == "📊 Dashboard" and role == 'superadmin':
        st.header("Rating Dashboard")
        st.markdown("🔴 **0-1**: Beginner | 🟡 **2**: Intermediate | 🟢 **3-4**: Proficient/Expert")
        if teams_list:
            sel_t, sel_d = render_team_selector("dash", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                df = load_matrix(sel_t, sel_d)
                if df.empty or len(df.columns) <= 2: st.info("No skill data available.")
                else:
                    heatmap_data = df.drop(columns=['Designation'], errors='ignore')
                    sk_cols = [c for c in heatmap_data.columns if c != 'Name']
                    def apply_color(val):
                        try:
                            v = int(float(val))
                            if v in [0, 1]: return 'background-color: #F8696B; color: black; font-weight: bold;'
                            elif v == 2: return 'background-color: #FFEB84; color: black; font-weight: bold;'
                            elif v in [3, 4]: return 'background-color: #63BE7B; color: black; font-weight: bold;'
                        except: pass
                        return ''
                    st.dataframe(heatmap_data.style.map(apply_color, subset=sk_cols), use_container_width=True, hide_index=True)

    # --- TAB 5: SKILL ANALYTICS (SUPERADMIN ONLY) ---
    elif selected_tab == "📈 Analytics" and role == 'superadmin':
        st.header("Skill Analytics")
        if teams_list:
            sel_t, sel_d = render_team_selector("stat", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                df = load_matrix(sel_t, sel_d)
                sk_cols = [c for c in df.columns if c not in ['Name', 'Designation']]
                if not sk_cols or df.empty: st.info("No skills to analyze.")
                else:
                    num_df = df.copy()
                    for c in sk_cols: num_df[c] = pd.to_numeric(num_df[c], errors='coerce').fillna(0).astype(int)
                    
                    st.subheader("1. Skill-wise Distribution")
                    sel_sk = st.selectbox("Select a Skill:", sk_cols)
                    sk_scores = num_df[['Name', sel_sk]].sort_values(by=sel_sk, ascending=False)
                    c1, c2 = st.columns([1, 2])
                    with c1: st.dataframe(sk_scores, hide_index=True, use_container_width=True)
                    with c2: st.bar_chart(sk_scores.set_index('Name'), color="#63BE7B")
                    
                    st.divider()
                    st.subheader("2. Top Performers (Scores > 0)")
                    t3 = []
                    for s in sk_cols:
                        sorted_d = num_df[['Name', s]].sort_values(by=s, ascending=False)
                        sorted_d = sorted_d[sorted_d[s] > 0] 
                        n, sc = sorted_d['Name'].tolist(), sorted_d[s].tolist()
                        t3.append({
                            "Skill": s, 
                            "1st": f"{n[0]} ({sc[0]})" if len(n)>0 else "-", 
                            "2nd": f"{n[1]} ({sc[1]})" if len(n)>1 else "-", 
                            "3rd": f"{n[2]} ({sc[2]})" if len(n)>2 else "-"
                        })
                    st.dataframe(pd.DataFrame(t3), hide_index=True, use_container_width=True)

    # --- TAB 6: TEAM HIERARCHY (SUPERADMIN ONLY) ---
    elif selected_tab == "🏢 Hierarchy" and role == 'superadmin':
        st.header("Team Hierarchy Setup")
        st.write("Manage your organizational structure below.")
        action_type = st.radio("Action:", ["Create a New Team", "Add Department to Existing Team"])
        with st.form("new_hierarchy_form", clear_on_submit=True):
            if action_type == "Create a New Team":
                has_dept = st.radio("Has departments?", ["No", "Yes"])
                new_t = st.text_input("New Team Name")
                new_d = st.text_input("Department Name") if has_dept == "Yes" else "None"
            else:
                new_t = st.selectbox("Existing Team", teams_list) if teams_list else None
                new_d = st.text_input("New Department Name")
            
            if st.form_submit_button("Create Structure"):
                if new_t and new_d:
                    if new_d == "None" and action_type == "Add Department to Existing Team": st.error("Provide a valid name.")
                    else:
                        add_to_directory(new_t, new_d)
                        st.session_state['flash_msg'] = "Structure created!"
                        time.sleep(1) # Sync delay fix
                        st.rerun()
        
        st.divider()
        st.subheader("Current Master Directory")
        st.write("Select a row and press Delete (or the trash icon) to remove it.")
        
        # Clean directory before rendering to prevent NaN crashes
        safe_dir = directory_df.dropna(how='all').fillna("")
        edited_dir = st.data_editor(safe_dir, hide_index=True, use_container_width=True, num_rows="dynamic", disabled=("Team", "Department"), key="dir_editor")
        
        if st.button("💾 Save Directory Changes", type="primary"):
            cleaned_dir = edited_dir[edited_dir['Team'].astype(str).str.strip() != ""]
            conn.update(worksheet="Directory", data=cleaned_dir)
            st.cache_data.clear()
            st.session_state['flash_msg'] = "Directory updated!"
            time.sleep(1)
            st.rerun()

    # --- TAB 7: CREDENTIALS (SUPERADMIN ONLY) ---
    elif selected_tab == "🔐 Credentials" and role == 'superadmin':
        st.header("Setup New User Credential")
        c_team, c_dept = None, None
        show_form = True
        
        c_role = st.selectbox("Assign Role", ["editor", "admin", "superadmin"])
        if c_role == "editor":
            existing = set(zip(creds_df[creds_df['Role']=='editor']['Team'], creds_df[creds_df['Role']=='editor']['Department']))
            all_combos = set(zip(directory_df['Team'], directory_df['Department']))
            avail = {(str(t), str(d)) for t, d in (all_combos - existing)}
            
            if not avail: 
                st.warning("All Team/Dept combos already have editors.")
                show_form = False
            else:
                c_team = st.selectbox("Assign Team", sorted(list(set([t for t, d in avail]))))
                avail_d = sorted([d for t, d in avail if str(t) == str(c_team)])
                if "None" in avail_d and len(avail_d) == 1: c_dept = "None"
                else: c_dept = st.selectbox("Assign Department", avail_d)
        elif c_role == "admin":
            existing = creds_df[creds_df['Role']=='admin']['Team'].tolist()
            avail = sorted([t for t in teams_list if t not in existing])
            if not avail: 
                st.warning("All Teams already have an admin.")
                show_form = False
            else:
                c_team, c_dept = st.selectbox("Assign Team Admin rights to:", avail), "All"
        else: 
            c_team, c_dept = "All", "All"

        if show_form and c_team is not None and c_dept is not None:
            with st.form("new_user_form", clear_on_submit=True):
                c_user = st.text_input("New Username")
                c_pass = st.text_input("New Password", type="password")
                if st.form_submit_button("Create Credential"):
                    if c_user and c_pass:
                        if add_credential(c_user, c_pass, c_role, c_team, c_dept):
                            st.session_state['flash_msg'] = f"Created {c_role} '{c_user}'!"
                            time.sleep(1)
                            st.rerun()
                        else: st.error("Username already exists!")

        st.divider()
        st.header("Credential List")
        view_df = creds_df.copy()
        cfg = {
            "Username": st.column_config.TextColumn("Username", required=True),
            "Password": st.column_config.TextColumn("Password (Visible)", required=True),
            "Role": st.column_config.SelectboxColumn("Role", options=["editor", "admin", "superadmin"], required=True),
            "Team": st.column_config.TextColumn("Team", required=True),
            "Department": st.column_config.TextColumn("Department", required=True)
        }
        
        edited_creds = st.data_editor(view_df, column_config=cfg, hide_index=True, use_container_width=True, num_rows="dynamic", key="role_editor")
        
        if st.button("💾 Save Credential Changes", type="primary"):
            # Sanitize data: completely remove empty lines to prevent crashes/wipeouts
            cleaned_creds = edited_creds.dropna(how='all').fillna("")
            cleaned_creds = cleaned_creds[cleaned_creds['Username'].astype(str).str.strip() != ""]
            
            if 'superadmin' not in cleaned_creds['Username'].astype(str).values: 
                st.error("Action Blocked: You cannot delete the master 'superadmin' account!")
            else:
                conn.update(worksheet="Credentials", data=cleaned_creds)
                st.cache_data.clear()
                st.session_state['flash_msg'] = "Credentials updated successfully!"
                time.sleep(1) # Sync delay fix
                st.rerun()

# --- EDITOR ROLE VIEW ---
else:
    my_dept = st.session_state['dept_access']
    st.info(f"You are editing the {get_display_name(my_team, my_dept)} Skill Matrix.")
    state_key = f"data_{my_team}_{my_dept}"
    if state_key not in st.session_state: st.session_state[state_key] = load_matrix(my_team, my_dept)
    display_team_matrix(my_team, my_dept, state_key)
