"""
Visualize the DIT-HAP data using JBrowse 2 within a Streamlit application.
"""

# ================================= Imports =================================
import streamlit as st

# ================================= Constants =================================
JBROWSE_IFRAME_URL = "https://dit-hap.github.io/"

# ================================= Functions =================================

@st.dialog("❓ How to Use This Tool", width="large")
def how_to_use_this_tool():
    """Dialog explaining how to use the JBrowse2 genome browser."""
    st.markdown("""
        **Step 1: Navigate the Genome**
        - Use the navigation bar to search for specific genes or genomic regions
        - Enter gene names (e.g., `cdc2`, `wee1`) or coordinates (e.g., `chrI:1000-5000`)
        - Zoom in/out using the mouse wheel or zoom controls
        - Click and drag to pan across the genome

        **Step 2: Explore Tracks**
        - **Forward insertion**: Transposon insertions in forward orientation
        - **Reverse insertion**: Transposon insertions in reverse orientation
        - Toggle track visibility using the track selection panel
        - Adjust track height and display settings as needed

        **Step 3: Analyze Genomic Context**
        - View gene annotations and exon-intron structures
        - Examine transposon insertion patterns within genes
        - Compare insertion density across different genomic regions
        - Correlate insertion patterns with gene essentiality data
        """)

@st.dialog("🔬 Understanding JBrowse2", width="large")
def understanding_jbrowse():
    """Dialog explaining JBrowse2 genome browser features."""
    st.markdown("""
        **What is JBrowse2?**

        JBrowse2 is a next-generation genome browser that provides:
        - **Interactive visualization**: Smooth zooming and panning across genomic regions
        - **Multiple track types**: Support for various data formats (BAM, BED, VCF, GFF, etc.)
        - **Real-time rendering**: Efficient data loading and display
        - **Customizable views**: Flexible track configuration and styling

        **Track Types in DIT-HAP:**
        - **Forward insertion**: Shows transposon insertion sites in forward orientation
        - **Reverse insertion**: Shows transposon insertion sites in reverse orientation
        - **Gene annotations**: Reference gene models from PomBase
        - **Genomic coordinates**: Chromosome positions and scale information

        **Visualization Features:**
        - **Linear view**: Traditional linear genome browser display
        - **Track stacking**: Multiple data tracks organized vertically
        - **Color coding**: Distinct colors for different data types
        - **Tooltips**: Hover over features for detailed information
        """)

@st.dialog("⚙️ Data Requirements", width="large")
def data_requirements():
    """Dialog explaining the data requirements for JBrowse2."""
    st.markdown("""
        **JBrowse2 Instance Requirements:**
        - **Hosted instance**: JBrowse2 server with configured data tracks
        - **Genome assembly**: Reference genome sequence for *S. pombe*
        - **Gene annotations**: PomBase gene models in GFF3/GTF format
        - **Insertion data**: Transposon insertion sites from DIT-HAP pipeline
        - **Track configuration**: JSON configuration files for track display

        **Data Integration:**
        - Forward and reverse insertion tracks processed from DIT-HAP outputs
        - Reference annotations from PomBase (version-specific)
        - Genome assembly matching pipeline reference
        - Indexed data files for efficient retrieval

        **Browser Setup:**
        - JBrowse2 instance hosted at https://dit-hap.github.io/
        - Data tracks pre-configured for DIT-HAP visualization
        - Responsive design for desktop and tablet viewing
        - Direct access to latest DIT-HAP genomic data
        """)

@st.dialog("🎯 Analysis Tips", width="large")
def analysis_tips():
    """Dialog providing analysis tips for JBrowse2 genome exploration."""
    st.markdown("""
        **Exploring Gene Regions:**
        - **Start with gene of interest**: Search for specific gene names or systematic IDs
        - **Zoom to appropriate level**: Overview (entire gene) or detailed (individual insertions)
        - **Check insertion distribution**: Look for patterns across gene bodies and regulatory regions
        - **Compare orientations**: Note differences between forward and reverse insertions

        **Interpreting Insertion Patterns:**
        - **Essential genes**: Fewer insertions due to negative selection
        - **Non-essential genes**: More uniform insertion distribution
        - **Hotspots**: Regions with high insertion density may indicate non-essential domains
        - **Coldspots**: Regions lacking insertions may indicate essential functional elements

        **Integration with Other Tools:**
        - **Depletion curves**: Genes identified in depletion analysis can be examined here
        - **Feature space**: Explore genomic context of gene clusters
        - **Enrichment results**: Investigate genomic organization of enriched gene sets
        - **Network analysis**: Correlate genomic position with network properties

        **Best Practices:**
        - Use systematic IDs for unambiguous gene identification
        - Verify gene orientation and strand information
        - Check multiple time points if available
        - Compare with reference annotations for validation
        """)

def main():
    """Main entry point for the JBrowse 2 page."""

    st.title("🧬 JBrowse 2 Genome Browser for Visualizing DIT-HAP Data")

    # Introduction and Usage Guide
    st.markdown("""
    ### 🔍 Interactive Genome Browser for DIT-HAP Data

    This page integrates the **JBrowse 2 genome browser** for visualizing DIT-HAP transposon insertion data.
    Explore genomic features, insertion patterns, and gene annotations in an interactive interface.
    """)

    if st.button("❓ How to Use This Tool"):
        how_to_use_this_tool()
    if st.button("🔬 Understanding JBrowse2"):
        understanding_jbrowse()
    if st.button("⚙️ Data Requirements"):
        data_requirements()
    if st.button("🎯 Analysis Tips"):
        analysis_tips()

    st.markdown("---")

    st.info(
        """
        You can also visit the JBrowse 2 instance directly at [DIT-HAP JBrowse 2](https://dit-hap.github.io/) which is hosted on GitHub Pages.
        """
    )
    st.warning(
        """
        **Available Tracks:** Forward insertion and reverse insertion
        """
    )
    
    # Embed JBrowse 2 using an iframe
    with st.container(border=True):
        st.components.v1.iframe(
            src=JBROWSE_IFRAME_URL,
            height=1000,
            scrolling=True
        )

if __name__ == "__main__":
    main()