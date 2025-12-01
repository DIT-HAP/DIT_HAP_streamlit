# ========================================== Import necessary libraries ==========================================
import streamlit as st

# ================================= Streamlit page configuration =================================
st.set_page_config(
    page_title="DIT-HAP Analysis Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="auto"
)

# ========================================== Define pages ==========================================
main_page = st.Page("pages/main.py", title="Home", icon=":material/home:")
plot_page = st.Page("pages/depletion_data.py", title="Depletion Curve", icon=":material/timeline:")
feature_space_page = st.Page("pages/feature_space.py", title="Feature space", icon=":material/scatter_plot:")
jbrowse2_page = st.Page("pages/jbrowse2.py", title="Genome Browser", icon=":material/align_center:")
enrichment_page = st.Page("pages/enrichment_analysis.py", title="Enrichment analysis", icon=":material/search_insights:")
go_cam_page = st.Page("pages/go_cam.py", title="GO-CAM Network", icon=":material/account_tree:")
verification_data_page = st.Page("pages/verification_data.py", title="Verification Data", icon=":material/free_cancellation:")

# ========================================== Set up navigation ==========================================
pg = st.navigation(
        {
            "Home": [main_page],
            "Visualization": [plot_page, feature_space_page, jbrowse2_page],
            "Analysis": [enrichment_page, go_cam_page],
            "Data": [verification_data_page],
        }
    )

# Run navigation
pg.run()


