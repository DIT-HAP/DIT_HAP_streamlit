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
    
    st.title("🧬 JBrowse 2 Genome Browser for Visualizing DIT-HAP Data")
    st.info(
        """
        This page integrates the JBrowse 2 genome browser to visualize DIT-HAP data.
        You can explore various genomic features and annotations using the interactive interface below.

        You can also visit the JBrowse 2 instance directly at DIT-HAP JBrowse 2 (https://dit-hap.github.io/) which is hosted on GitHub Pages.
        """
    )
    st.warning(
        """
        Forward insertion and reverse insertion
        """
    )
    
    # Embed JBrowse 2 using an iframe
    with st.container(border=True):
        st.components.v1.iframe(
            src=JBROWSE_IFRAME_URL,
            height=2000,
            scrolling=True
        )

if __name__ == "__main__":
    main()