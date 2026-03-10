import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Skill Matrix", layout="wide")
st.title("Interactive Skill Matrix")

# 2. Initialize Data in Session State
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

# Create two distinct pages/tabs
tab1, tab2 = st.tabs(["📝 Data Entry & Definitions", "📊 Heatmap Dashboard"])

with tab1:
    st.header("Skill Level Definitions")
    
    # Replicating your ReadMe definitions
    st.markdown("""
    | Score | Skill Level | Description |
    | :--- | :--- | :--- |
    | **4** | **Expert** | Fully Capable & Experienced. Sought for help by other departments. Needs no assistance. |
    | **3** | **Proficient** | Capable & Experienced. Able to work independently with little help. |
    | **2** | **Intermediate** | Able to perform. Has some experience. Needs help from time to time. |
    | **1** | **Beginner** | Limited Knowledge. Cannot work on critical tasks. Needs significant help. |
    | **0** | **No Knowledge** | No knowledge & Experience. |
    """)
    
    st.divider()
    st.subheader("Update Team Scores")
    st.write("Edit the scores below using the dropdowns. Your changes will immediately reflect on the Heatmap tab.")
    
    df = st.session_state['skill_data']
    skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]

    # Setup dropdowns for 0-4
    column_config = {
        col: st.column_config.SelectboxColumn(
            col,
            help=f"Select score (0 to 4)",
            options=[0, 1, 2, 3, 4],
            required=True
        )
        for col in skill_cols
    }

    # Data editor UI
    edited_df = st.data_editor(
        df, 
        column_config=column_config, 
        hide_index=True,
        use_container_width=True,
        height=300
    )

with tab2:
    st.header("Team Heatmap")
    st.markdown("🔴 **0-1**: Beginner/No Knowledge | 🟡 **2**: Intermediate | 🟢 **3-4**: Proficient/Expert")
    
    # Prepare data for heatmap
    heatmap_data = edited_df.set_index('Name').drop(columns=['Designation'])

    # Apply the traffic-light color logic directly to the dataframe
    def apply_color_logic(val):
        if val in [0, 1]:
            return 'background-color: #F8696B; color: black; font-weight: bold;' # Red
        elif val == 2:
            return 'background-color: #FFEB84; color: black; font-weight: bold;' # Yellow
        elif val in [3, 4]:
            return 'background-color: #63BE7B; color: black; font-weight: bold;' # Green
        return ''

    styled_heatmap = heatmap_data.style.map(apply_color_logic)

    # Display the heatmap
    st.dataframe(styled_heatmap, use_container_width=True, height=400)
