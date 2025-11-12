import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="DIT-HAP Analysis Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="auto"
)

# Define pages
main_page = st.Page("pages/main.py", title="Home", icon=":material/home:")
plot_page = st.Page("pages/depletion_data.py", title="Curve plot", icon=":material/timeline:")
feature_space_page = st.Page("pages/feature_space.py", title="Feature space", icon=":material/scatter_plot:")
enrichment_page = st.Page("pages/enrichment_analysis.py", title="Enrichment analysis", icon=":material/search_insights:")

# Create navigation
pg = st.navigation(
        {
            "Home": [main_page],
            "Visualization": [plot_page, feature_space_page],
            "Analysis": [enrichment_page],
        }
    )

# Run navigation
pg.run()


