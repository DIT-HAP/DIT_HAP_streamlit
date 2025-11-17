"""
Visualize the DIT-HAP data using JBrowse 2 within a Streamlit application.
"""

# ================================= Imports =================================
import streamlit as st

# ================================= Constants =================================
JBROWSE_IFRAME_URL = "https://dit-hap.github.io/"

# ================================= Functions =================================
def main():
    """Main entry point for the JBrowse 2 page."""
    
    st.title("JBrowse 2 Genome Browser")
    st.markdown(
        """
        This page integrates the JBrowse 2 genome browser to visualize genomic data.
        You can explore various genomic features and annotations using the interactive interface below.
        """
    )
    
    # Embed JBrowse 2 using an iframe
    st.components.v1.iframe(
        src=JBROWSE_IFRAME_URL,
        height=4000,
        scrolling=True
    )

if __name__ == "__main__":
    main()