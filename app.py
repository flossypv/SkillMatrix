if 'uiux_data' not in st.session_state:
    uiux_data = {
        'Name': ['Ambika', 'Prabavathy'], 
        'Designation': ['Full Stack Developer', 'Frontend Developer'], 
        'PHP': [3, 0], 'Wordpress': [3, 3], 'JavaScript': [3, 2], 'HTML': [3, 3], 'CSS': [2, 3], 'MySQL': [3, 0], 'SQL': [2, 0]
    }
    st.session_state['uiux_data'] = pd.DataFrame(uiux_data)
