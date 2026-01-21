"""
Feature space page for DIT-HAP Streamlit application.

This page provides a visualization of the query genes in the feature space.
"""

# ================================= Imports =================================
import streamlit as st
import sys
import pandas as pd
import altair as alt
sys.path.append("../src")
from src.preparation import sidebar_gene_input
from src.data_config import get_default_config
from src.data_manager import load_gene_metadata, load_gene_level_stats, GeneLevelData

# ================================= Functions =================================

@st.dialog("❓ How to Use This Tool", width="large")
def how_to_use_this_tool():
    """Dialog explaining how to use the feature space visualization tool."""
    st.markdown("""
        **Step 1: Enter Genes** (Sidebar)
        - Input gene names (e.g., `cdc2`, `wee1`) or systematic IDs (e.g., `SPAC1002.09c`)
        - Separate multiple genes with commas or newlines
        - Click "Submit" to visualize your genes in feature space

        **Step 2: Interpret the Plot**
        - **X-axis (Depletion rate)**: How quickly genes are depleted over time (mu parameter)
        - **Y-axis (Depletion lag)**: Time delay before depletion begins (lambda parameter)
        - **Gray circles**: Background genes (all genes in the dataset)
        - **Red circles**: Your query genes (highlighted for comparison)

        **Step 3: Analyze Patterns**
        - **Essential genes**: Typically show high depletion rates (right side of plot)
        - **Non-essential genes**: Lower depletion rates (left side of plot)
        - **Gene clusters**: Query genes with similar statistical profiles appear grouped together
        - **Outliers**: Genes with unusual depletion patterns may indicate unique biology
        """)

@st.dialog("🔬 Understanding Feature Space", width="large")
def understanding_feature_space():
    """Dialog explaining the feature space visualization."""
    st.markdown("""
        **What is Feature Space?**

        Feature space visualization places genes in a 2D plot based on their statistical properties from the DIT-HAP pipeline:
        - **Depletion rate (mu)**: The rate at which transposon insertions in a gene decrease over time
        - **Depletion lag (lambda)**: The time delay before depletion begins

        **Interpreting the Plot:**
        - **Upper right**: High depletion rate, long lag → Genes that deplete quickly but after a delay
        - **Lower right**: High depletion rate, short lag → Rapidly depleting essential genes
        - **Upper left**: Low depletion rate, long lag → Slow depletion with delayed onset
        - **Lower left**: Low depletion rate, short lag → Non-essential genes with minimal depletion

        **Biological Meaning:**
        - **Essential genes**: Higher depletion rates indicate negative fitness effects
        - **Non-essential genes**: Lower depletion rates suggest neutral fitness effects
        - **Condition-specific genes**: May show intermediate patterns depending on experimental conditions
        """)

@st.dialog("⚙️ Data Requirements", width="large")
def data_requirements():
    """Dialog explaining the data requirements for feature space visualization."""
    st.markdown("""
        **Required DIT-HAP Pipeline Outputs:**
        - Gene-level fitting results containing mu and lambda parameters
        - Gene-level statistics from DIT-HAP pipeline analysis
        - Gene metadata for name/ID conversion
        - Reference genome annotations from PomBase

        **Statistical Parameters:**
        - **mu (μ)**: Depletion rate parameter from model fitting
        - **lambda (λ)**: Depletion lag parameter from model fitting
        - Model fitting quality metrics for confidence assessment
        - Time course data from standard DIT-HAP pipeline

        **Data Organization:**
        - Files should follow standard DIT-HAP pipeline structure
        - Proper naming conventions required for automatic detection
        - Default dataset configuration used for feature space analysis
        """)

@st.dialog("🎯 Analysis Tips", width="large")
def analysis_tips():
    """Dialog providing analysis tips for interpreting feature space visualizations."""
    st.markdown("""
        **Gene Selection Strategies:**
        - **Essential genes**: Select genes showing strong depletion in depletion curves
        - **Pathway genes**: Choose genes from the same biological pathway
        - **Cluster genes**: Use genes identified from clustering analysis
        - **Differential genes**: Compare genes from different experimental conditions

        **Interpreting Patterns:**
        - **Tightly grouped genes**: Share similar depletion characteristics
        - **Scattered genes**: Diverse fitness effects within your gene set
        - **Overlap with background**: Query genes similar to population average
        - **Outliers**: May indicate unique biological properties or data quality issues

        **Comparative Analysis:**
        - Compare gene positions across different experimental conditions
        - Look for shifts in feature space indicating condition-specific effects
        - Use feature space to validate gene essentiality predictions
        - Cross-reference with enrichment analysis results
        """)

def load_data():
    """Load only the data needed for feature space analysis."""
    
    # Get default configuration
    config = get_default_config()
    
    # Validate configuration
    config.validate_all_paths()
    
    # Load only the required data categories
    with st.spinner("Loading gene metadata...", show_time=True):
        gene_metadata = load_gene_metadata(config.gene_metadata)

    with st.spinner("Loading gene level statistics...", show_time=True):
        gene_level = load_gene_level_stats(config.gene_level)
    
    return gene_metadata, gene_level

def display_feature_space(query_genes: list[str], gene_level: GeneLevelData) -> alt.LayerChart:
    """Display the feature space for the query genes."""

    all_gene_feature_space = alt.Chart(gene_level.gene_level_fitting_results).mark_circle(opacity=0.6).encode(
        x=alt.X("um:Q", title="Depletion rate"),
        y=alt.Y("lam:Q", title="Depletion lag"),
        color=alt.value("lightgray"),
        tooltip=gene_level.gene_level_fitting_results.columns.tolist()
    )

    query_gene_feature_space = alt.Chart(gene_level.gene_level_fitting_results.loc[query_genes]).mark_circle(opacity=0.6).encode(
        x=alt.X("um:Q", title="Depletion rate"),
        y=alt.Y("lam:Q", title="Depletion lag"),
        color=alt.value("red"),
        tooltip=gene_level.gene_level_fitting_results.columns.tolist()
    )

    return all_gene_feature_space + query_gene_feature_space

def main():
    """Main entry point for the feature space page."""

    st.title(":chart_with_upwards_trend: Feature Space Visualization")

    # Introduction and Usage Guide
    st.markdown("""
    ### 📊 Multi-Dimensional Feature Space Analysis

    This page provides **interactive visualization of genes in feature space** based on statistical parameters from the **[DIT-HAP pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)**. Explore how your genes of interest compare to the genome-wide distribution.
    """)

    usage_guides = {
        "❓ How to Use This Tool": how_to_use_this_tool,
        "🔬 Understanding Feature Space": understanding_feature_space,
        "⚙️ Data Requirements": data_requirements,
        "🎯 Analysis Tips": analysis_tips
    }
    st.segmented_control(
        label="📖 Usage Guides",
        options=list(usage_guides.keys()),
        key="usage_guide_selector",
        on_change=lambda: usage_guides[st.session_state.usage_guide_selector](),
        width="stretch",
        label_visibility="collapsed"
    )

    # Load required data
    gene_metadata, gene_level = load_data()
    
    # Get gene input from sidebar
    covered_gene_sysIDs, submit_button = sidebar_gene_input(
        gene_metadata.gene_info_with_essentiality, 
        gene_level.gene_level_LFCs
    )
    
    if submit_button and covered_gene_sysIDs:

        bg_genes = gene_level.gene_level_LFCs.index.tolist()

        alt_chart = display_feature_space(covered_gene_sysIDs, gene_level)
        st.altair_chart(alt_chart, width="content")

if __name__ == "__main__":
    main()