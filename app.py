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
            time.sleep(2) 
    except Exception:
        pass

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
    if username.strip() in creds_df['Username'].astype(str).str.strip().values: return False
    new_user = pd.DataFrame([{"Username": username.strip(), "Password": password.strip(), "Role": role, "Team": team.strip(), "Department": dept.strip()}])
    updated_creds = pd.concat([creds_df, new_user], ignore_index=True)
    conn.update(worksheet="Credentials", data=updated_creds)
    st.cache_data.clear() 
    return True

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

def get_sheet_name(team, dept): return str(team).strip() if str(dept).strip() == "None" else f"{str(team).strip()}_{str(dept).strip()}"
def get_display_name(team, dept): return str(team).strip() if str(dept).strip() == "None" else f"{str(team).strip()} - {str(dept).strip()}"

def load_matrix(team, dept):
    sheet_name = get_sheet_name(team, dept)
    try:
        df = conn.read(worksheet=sheet_name, ttl=0).dropna(how='all', axis=1).dropna(how='all', axis=0)
        if df.empty: raise Exception("Empty Matrix")
    except Exception:
        if str(team).strip() == "Canyon" and str(dept).strip() == "QA": df = pd.DataFrame(default_qa)
        elif str(team).strip() == "Canyon" and str(dept).strip() == "UIUX": df = pd.DataFrame(default_uiux)
        elif str(team).strip() == "Canyon" and str(dept).strip() == "Dev": df = pd.DataFrame(default_dev)
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
        st.markdown("# 🚀 AppDevelopment SkillMatrix")
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
        st.markdown('<div style="border-left: 2px solid rgba(128, 128, 128, 0.2); min-height: 550px; height: 100%; margin: 0 auto;"></div>', unsafe_allow_html=True)

    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        st.subheader("🔐 Secure Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In", use_container_width=True)
            if submit:
                try:
                    creds_df = load_credentials()
                    user_row = creds_df[creds_df['Username'].astype(str).str.strip() == str(username).strip()]
                    if not user_row.empty and str(user_row.iloc[0]['Password']).strip() == password.strip():
                        st.session_state['authenticated'] = True
                        st.session_state['role'] = str(user_row.iloc[0]['Role']).strip()
                        st.session_state['username'] = str(username).strip()
                        st.session_state['team_access'] = str(user_row.iloc[0]['Team']).strip()
                        st.session_state['dept_access'] = str(user_row.iloc[0]['Department']).strip()
                        # LANDING PAGE LOGIC: Set Dashboard as default after login
                        st.session_state["admin_nav"] = "📊 Dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                except Exception:
                    st.error("Error connecting to database.")
    st.stop()

# --- GLOBAL VARIABLES ---
role = st.session_state['role']
my_team = st.session_state['team_access']
my_dept = st.session_state['dept_access']
username = st.session_state['username']

# --- SIDEBAR MENU & PROFILE ---
st.sidebar.markdown(f"### 👋 Welcome, **{username}**!")
st.sidebar.caption(f"**Access:** {role.capitalize()}")
if role != 'superadmin':
    st.sidebar.caption(f"**Team:** {my_team}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    for key in ['authenticated', 'role', 'username', 'team_access', 'dept_access', 'admin_nav']: 
        st.session_state[key] = None
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("## 🧭 Menu")

if role in ['superadmin', 'admin']:
    nav_options = ["📊 Dashboard", "📈 Analytics", "📝 Matrix Editor", "👤 Members", "🎯 Skills"]
    if role == 'superadmin':
        nav_options += ["🏢 Hierarchy", "🔐 Credentials"]
    
    # Initialize session state if not set
    if "admin_nav" not in st.session_state:
        st.session_state["admin_nav"] = "📊 Dashboard"
    
    selected_tab = st.sidebar.radio("Select View", nav_options, key="admin_nav", label_visibility="collapsed")
else:
    selected_tab = "📝 Matrix Editor"

# --- MAIN APP HEADER ---
st.title(selected_tab)
st.divider()

if 'flash_msg' in st.session_state:
    st.success(st.session_state['flash_msg'])
    del st.session_state['flash_msg']

def render_team_selector(prefix, role, my_team, teams_list, directory_df):
    colA, colB = st.columns(2)
    if role == 'superadmin':
        selected_team = colA.selectbox("Select Team:", teams_list, key=f"{prefix}_t")
    else:
        selected_team = my_team
        colA.write(f"**Team:** {selected_team}")
    if not selected_team: return None, None
    depts = directory_df[directory_df['Team'] == selected_team]['Department'].unique().tolist()
    valid_depts = sorted([d for d in depts if str(d).strip() not in ["None", "", "nan"]])
    if not valid_depts: return selected_team, "None"
    selected_dept = colB.selectbox("Select Department:", valid_depts, key=f"{prefix}_d")
    return selected_team, selected_dept

try:
    if role in ['superadmin', 'admin']:
        directory_df = load_directory()
        creds_df = load_credentials()
        directory_df['Team'] = directory_df['Team'].astype(str).str.strip()
        directory_df['Department'] = directory_df['Department'].astype(str).str.strip()
        teams_list = directory_df['Team'].unique().tolist() if role == 'superadmin' else [my_team]

        # --- LANDING PAGE: DASHBOARD ---
        if selected_tab == "📊 Dashboard":
            if teams_list:
                sel_t, sel_d = render_team_selector("dash", role, my_team, teams_list, directory_df)
                if sel_t and sel_d:
                    df = load_matrix(sel_t, sel_d)
                    if df.empty or len(df.columns) <= 2: st.info("No skill data available.")
                    else:
                        sk_cols = [c for c in df.columns if c not in ['Name', 'Designation']]
                        avg_val = df[sk_cols].mean().mean()
                        top_skill = df[sk_cols].mean().idxmax()
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Team Strength", f"{avg_val:.2f} / 4")
                        m2.metric("Strongest Asset", top_skill)
                        m3.metric("Headcount", len(df))
                        st.divider()
                        st.markdown("🔴 **0-1**: Beginner | 🟡 **2**: Intermediate | 🟢 **3-4**: Expert")
                        heatmap_data = df.drop(columns=['Designation'], errors='ignore')
                        def apply_color(val):
                            try:
                                v = int(float(val))
                                if v in [0, 1]: return 'background-color: #ff4b4b; color: white;'
                                elif v == 2: return 'background-color: #ffa500; color: white;'
                                elif v in [3, 4]: return 'background-color: #00c853; color: white;'
                            except: pass
                            return ''
                        st.dataframe(heatmap_data.style.map(apply_color, subset=sk_cols), use_container_width=True, hide_index=True, height=350)

        # --- COMPACT ANALYTICS ---
        elif selected_tab == "📈 Analytics":
            if teams_list:
                sel_t, sel_d = render_team_selector("stat", role, my_team, teams_list, directory_df)
                if sel_t and sel_d:
                    df = load_matrix(sel_t, sel_d)
                    sk_cols = [c for c in df.columns if c not in ['Name', 'Designation']]
                    if not sk_cols or df.empty: st.info("No skills to analyze.")
                    else:
                        num_df = df.copy()
                        for c in sk_cols: num_df[c] = pd.to_numeric(num_df[c], errors='coerce').fillna(0).astype(int)
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.subheader("🎯 Skill Focus")
                            sel_sk = st.selectbox("Pick a Skill", sk_cols)
                            sk_scores = num_df[['Name', sel_sk]].sort_values(by=sel_sk, ascending=False)
                            expert = sk_scores.iloc[0]
                            st.success(f"**Top Expert:** \n{expert['Name']} ({expert[sel_sk]})")
                        with c2:
                            st.bar_chart(sk_scores.set_index('Name'), color="#2ecc71")
                        st.divider()
                        st.subheader("🏆 Category Champions")
                        leaders = []
                        for s in sk_cols:
                            sorted_d = num_df[['Name', s]].sort_values(by=s, ascending=False).query(f"`{s}` > 0")
                            names = sorted_d['Name'].tolist()
                            scores = sorted_d[s].tolist()
                            leaders.append({
                                "Skill": s,
                                "🥇 1st Place": f"{names[0]} ({scores[0]})" if names else "-",
                                "🥈 2nd Place": f"{names[1]} ({scores[1]})" if len(names)>1 else "-",
                                "Avg": round(num_df[s].mean(), 1)
                            })
                        st.table(pd.DataFrame(leaders))

        # --- OTHER TABS (Condensed for brevity) ---
        elif selected_tab == "📝 Matrix Editor":
            sel_t, sel_d = render_team_selector("edit", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                state_key = f"data_{sel_t}_{sel_d}"
                if state_key not in st.session_state: st.session_state[state_key] = load_matrix(sel_t, sel_d)
                df = st.session_state[state_key]
                sk_cols = [c for c in df.columns if c not in ['Name', 'Designation']]
                col_cfg = {c: st.column_config.SelectboxColumn(c, options=[0,1,2,3,4], required=True) for c in sk_cols}
                edited_df = st.data_editor(df, column_config=col_cfg, hide_index=True, use_container_width=True)
                if st.button("💾 Save Scores", type="primary"):
                    save_matrix(sel_t, sel_d, edited_df)
                    st.session_state['flash_msg'] = "Scores saved!"
                    st.rerun()

        elif selected_tab == "👤 Members":
            sel_t, sel_d = render_team_selector("mem", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                df = load_matrix(sel_t, sel_d)
                col1, col2 = st.columns(2)
                with col1:
                    with st.form("add_mem"):
                        n, d = st.text_input("Name"), st.text_input("Designation")
                        if st.form_submit_button("Add Member") and n:
                            new_row = {'Name': n, 'Designation': d}
                            for c in df.columns: 
                                if c not in ['Name', 'Designation']: new_row[c] = 0
                            save_matrix(sel_t, sel_d, pd.concat([df, pd.DataFrame([new_row])], ignore_index=True))
                            st.rerun()
                with col2:
                    with st.form("del_mem"):
                        m = st.selectbox("Select Member", df['Name'].tolist()) if not df.empty else None
                        if st.form_submit_button("Delete Member") and m:
                            save_matrix(sel_t, sel_d, df[df['Name'] != m])
                            st.rerun()

        elif selected_tab == "🎯 Skills":
            sel_t, sel_d = render_team_selector("skil", role, my_team, teams_list, directory_df)
            if sel_t and sel_d:
                df = load_matrix(sel_t, sel_d)
                col1, col2 = st.columns(2)
                with col1:
                    with st.form("add_sk"):
                        s = st.text_input("Skill Name")
                        if st.form_submit_button("Add Skill") and s:
                            df[s] = 0
                            save_matrix(sel_t, sel_d, df)
                            st.rerun()
                with col2:
                    with st.form("del_sk"):
                        sk_list = [c for c in df.columns if c not in ['Name', 'Designation']]
                        s = st.selectbox("Select Skill", sk_list) if sk_list else None
                        if st.form_submit_button("Delete Skill") and s:
                            save_matrix(sel_t, sel_d, df.drop(columns=[s]))
                            st.rerun()

        elif selected_tab == "🏢 Hierarchy" and role == 'superadmin':
            act = st.radio("Action:", ["Create New Team", "Add Dept"])
            with st.form("hier"):
                t_input = st.text_input("Team Name")
                d_input = st.text_input("Dept Name") if act == "Add Dept" else "None"
                if st.form_submit_button("Submit"):
                    add_to_directory(t_input, d_input)
                    st.rerun()

        elif selected_tab == "🔐 Credentials" and role in ['superadmin', 'admin']:
            with st.form("cred"):
                u, p = st.text_input("Username"), st.text_input("Password", type="password")
                r = st.selectbox("Role", ["editor", "admin"])
                if st.form_submit_button("Create"):
                    add_credential(u, p, r, my_team, "All")
                    st.rerun()

    else:
        # Editor-only simple view
        df = load_matrix(my_team, my_dept)
        st.subheader(f"Editing {my_team} - {my_dept}")
        edited = st.data_editor(df, use_container_width=True)
        if st.button("Save"):
            save_matrix(my_team, my_dept, edited)
            st.success("Saved!")

except Exception as e:
    st.error(f"Error: {str(e)}")
