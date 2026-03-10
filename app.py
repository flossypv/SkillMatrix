import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

# 1. Page Configuration
st.set_page_config(page_title="Skill Matrix Dashboard", layout="wide")
st.title("Interactive Skill Matrix Dashboard")
st.markdown("Edit the scores directly in the table below using the **dropdown menus (0-4)**. The heatmap will automatically update to reflect your changes!")

# 2. Initialize Data in Session State
# This ensures the data isn't reset every time you interact with the app
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

df = st.session_state['skill_data']

# 3. Interactive Data Editor (Dropdowns)
st.subheader("📝 Data Entry (Dropdowns for 0-4)")

# Identify skill columns (everything except Name and Designation)
skill_cols = [col for col in df.columns if col not in ['Name', 'Designation']]

# Configure the columns to be Selectboxes limiting input from 0 to 4
column_config = {
    col: st.column_config.SelectboxColumn(
        col,
        help=f"Select score for {col} (0=None, 4=Expert)",
        options=[0, 1, 2, 3, 4],
        required=True
    )
    for col in skill_cols
}

# Display the editor and save the changes back to a new dataframe
edited_df = st.data_editor(
    df, 
    column_config=column_config, 
    hide_index=True,
    use_container_width=True
)

# 4. Auto-updating Heatmap Visualization
st.subheader("📊 Live Heatmap (Headers on Top)")

# Prepare data for heatmap: set index to Name and drop Designation
heatmap_data = edited_df.set_index('Name').drop(columns=['Designation'])

# Define Custom Colormap (Red=0, Yellow=2, Green=4)
colors = ["#F8696B", "#FFEB84", "#63BE7B"]
cmap = LinearSegmentedColormap.from_list("custom_heatmap", colors, N=5)

# Initialize Matplotlib Figure
fig, ax = plt.subplots(figsize=(18, 7))

# Generate the Heatmap
sns.heatmap(heatmap_data, annot=True, cmap=cmap, cbar=False, 
            linewidths=1, linecolor='lightgray', 
            vmin=0, vmax=4, annot_kws={"size": 11, "weight": "bold"}, ax=ax)

# Move X-axis (Technical Skills) to the top
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

# Formatting Labels and Titles
plt.xlabel("Technical Skills", fontsize=13, labelpad=15, fontweight='bold')
plt.ylabel("Team Members", fontsize=13, labelpad=10, fontweight='bold')

# Rotate X-axis labels to prevent overlap
plt.xticks(rotation=45, ha='left', fontsize=11)
plt.yticks(rotation=0, fontsize=11)

# Adding the Legend
legend_elements = [
    Patch(facecolor="#F8696B", label='0 - No knowledge / 1 - Beginner'),
    Patch(facecolor="#FFEB84", label='2 - Intermediate'),
    Patch(facecolor="#63BE7B", label='3 - Proficient / 4 - Expert')
]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=11)

plt.tight_layout()

# Render the plot in Streamlit
st.pyplot(fig)
