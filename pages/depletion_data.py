"""
Updated plot page using the new modular data loading architecture.

This version demonstrates how to use the new simplified data loading
system with modular configuration.
"""

# ================================= Imports =================================
import streamlit as st
import altair as alt
import pandas as pd
import sys
sys.path.append("../src")
from src.preparation import sidebar_gene_input
from src.data_config import get_default_config, get_long_timecourse_config, get_haploid_config, DataConfig
from src.data_manager import load_gene_metadata, load_insertion_level_stats, load_gene_level_stats, GeneMetadataData, InsertionLevelData, GeneLevelData
from src.get_gene_data import get_gene_info, get_gene_body, get_insertion_level_data, get_gene_level_data
from src.display_gene_data import display_basic_information, display_gene_body, display_insertion_level_data, display_gene_level_data, combine_plots, display_gene_level_metrics

# ================================= Constants =================================
P_VALUE_THRESHOLD = 0.05

TIME_POINTS = {
    "YES0": 0,
    "YES1": 2.352,
    "YES2": 5.588,
    "YES3": 9.104,
    "YES4": 12.480
}

TIME_POINTS_LONG_TIMECOURSE = {
    "YES0": 0,
    "YES1": 3.723,
    "YES2": 6.969,
    "YES3": 10.104,
    "YES4": 13.554,
    "YES5": 17.098,
    "YES6": 20.059
}

TIME_POINTS_HAPLOID = {
    "0h": 0,
    "YES0": 0.553,
    "YES1": 2.097,
    "YES2": 5.629,
    "YES3": 8.831,
    "YES4": 12.203,
    "YES5": 15.818,
    "YES6": 19.081
}

# ================================= Functions =================================

def load_depletion_data(config: DataConfig) -> tuple[GeneMetadataData, InsertionLevelData, GeneLevelData]:
    """Load only the data needed for depletion analysis."""
    
    # Validate configuration
    config.validate_all_paths()
    
    # Load only the required data categories
    with st.spinner("Loading gene metadata...", show_time=True):
        gene_metadata = load_gene_metadata(config.gene_metadata)
    
    with st.spinner("Loading insertion level statistics...", show_time=True):
        insertion_level = load_insertion_level_stats(config.insertion_level)
    
    with st.spinner("Loading gene level statistics...", show_time=True):
        gene_level = load_gene_level_stats(config.gene_level)
    
    return gene_metadata, insertion_level, gene_level

def get_gene_result(
    gene: str,
    gene_length: int,
    timepoints: dict,
    insertion_level: InsertionLevelData,
    gene_level: GeneLevelData,
    gene_body_plot: alt.LayerChart
) -> tuple[pd.DataFrame | None, alt.VConcatChart | None, bool]:
    """Get the gene result for a given gene."""
    try:
        insertion_level_anno_and_results, insertion_level_data = get_insertion_level_data(gene, insertion_level, timepoints)
        gene_level_fitting_results_in_current_gene, gene_level_data = get_gene_level_data(gene, gene_level, timepoints)
        
        insertion_level_data_plot1, insertion_level_data_plot2 = display_insertion_level_data(
            gene_length, 
            insertion_level_anno_and_results, 
            insertion_level_data,
            timepoints
        )
        
        gene_level_DR_line, gene_level_data_plot, DL_line_plot, DR_line_plot, fitting_curve_plot = display_gene_level_data(
            gene_level_fitting_results_in_current_gene, 
            gene_level_data,
            timepoints
        )

        combined_plot = combine_plots(
            gene_body_plot, 
            insertion_level_data_plot1, 
            insertion_level_data_plot2, 
            gene_level_DR_line, 
            gene_level_data_plot, 
            DL_line_plot, 
            DR_line_plot, 
            fitting_curve_plot
        )

        return gene_level_fitting_results_in_current_gene, combined_plot, True
    except Exception as e:
        return None, None, False
    
@st.dialog("❓ How to use this tool", width="large")
def how_to_use_this_tool():
    """Dialog explaining how to use the depletion data visualization tool."""
    st.markdown("""
        **Step 1: Enter Genes** (Sidebar)
        - Input gene names (e.g., `cdc2`, `wee1`) or systematic IDs (e.g., `SPAC1002.09c`)
        - Separate multiple genes with commas or newlines
        - Click "Submit" to analyze your genes

        **Step 2: Review Results**
        - **Basic Information**: Gene name, systematic ID, essentiality status
        - **Gene Structure**: Genomic coordinates and orientation
        - **Insertion-Level Data**: Individual transposon insertion statistics and quality metrics
        - **Gene-Level Analysis**: Depletion curves and fitness measurements across time points
        - **Statistical Models**: Curve fitting results with confidence intervals

        **Step 3: Compare Datasets**
        - **Standard Pipeline**: Regular diploid DIT-HAP analysis (4 time points)
        - **Long Timecourse**: Extended temporal resolution (6 time points)
        - **Haploid Analysis**: Single-chromosome fitness profiling

        **Step 4: Interpret Results**
        - **Downward depletion curves**: Gene is essential/fit-negative
        - **Flat/no depletion**: Gene is non-essential/fit-neutral
        - **Steeper slopes**: Stronger fitness effects
        - **Error bars**: Statistical confidence in measurements
        """)
    
@st.dialog("🔬 Understanding the Plots", width="large")
def understanding_plots():
    """Dialog explaining the different plots shown in the depletion data visualization."""
    st.markdown("""
        **Gene Structure Panel:**
        - Shows genomic location, strand orientation, and coding regions
        - Transposon insertion sites mapped to gene coordinates
        - Color-coded by insertion effects (positive/negative fitness)

        **Insertion-Level Statistics:**
        - **Base Mean**: Read count normalization for each insertion
        - **Log Fold Change (LFC)**: Fitness effect of individual insertions
        - **Transformed Weights**: Statistical confidence for each insertion
        - **Quality Metrics**: Model fitting and imputation statistics

        **Gene-Level Depletion Curves:**
        - **DR Line (Depletion Rate)**: Rate of gene loss over time
        - **DL Line (Depletion Level)**: Relative abundance of insertions
        - **Fitting Curve**: Statistical model of depletion kinetics
        - **Confidence Intervals**: Statistical uncertainty estimates
        """)
    
@st.dialog("⚙️ Data Requirements", width="large")
def data_requirements():
    """Dialog explaining the data requirements for the depletion data visualization."""
    st.markdown("""
        **Required DIT-HAP Pipeline Outputs:**
        - Gene essentiality classifications from pipeline
        - Insertion-level statistics (baseMean, LFC, fitting results)
        - Gene-level depletion measurements across time points
        - Quality control and imputation metrics
        - Reference genome annotations from PomBase

        **Data Organization:**
        - Files should follow standard DIT-HAP pipeline structure
        - Proper naming conventions required for automatic detection
        - Multiple dataset configurations supported (default, long timecourse, haploid)
        - Reference data must be present for gene annotations
        """)

@st.dialog("🎯  Analysis Tips", width="large")
def analysis_tips():
    """Dialog providing analysis tips for interpreting depletion data."""
    st.markdown("""
        **Interpreting Depletion Curves:**
        - **Downward Trends**: Indicate essential genes with negative fitness effects
        - **Flat Curves**: Suggest non-essential genes with neutral fitness
        - **Steepness of Slope**: Reflects strength of fitness impact
        - **Error Bars**: Represent statistical confidence in measurements

        **Comparing Datasets:**
        - Analyze differences between standard, long timecourse, and haploid datasets
        - Look for consistent patterns across different experimental setups

        **Statistical Considerations:**
        - Pay attention to p-values and confidence intervals
        - Consider biological relevance alongside statistical significance
        """)


def main():
    """Main entry point for the depletion data page."""

    # with st.container(border=True):
    #     col1, col2, col3, col4 = st.columns(4)
    #     with col1:
    #         if st.button("❓ How to Use This Tool"):
    #             how_to_use_this_tool()
    #     with col2:
    #         if st.button("🔬 Understanding the Plots"):
    #             understanding_plots()
    #     with col3:
    #         if st.button("⚙️ Data Requirements"):
    #             data_requirements()
    #     with col4:
    #         if st.button("🎯 Analysis Tips"):
    #             analysis_tips()

    

    st.title(":chart_with_upwards_trend: Depletion Data Visualization")

    # Introduction and Usage Guide
    st.markdown("""
    ### 🧬 Gene Depletion Analysis for DIT-HAP Pipeline Results

    This page provides **interactive visualization of gene depletion curves** generated by the **[DIT-HAP pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)**.
    Analyze how individual genes respond to transposon insertions over multiple time courses.
    """)

    usage_guides = {
        "❓ How to Use This Tool": how_to_use_this_tool,
        "🔬 Understanding the Plots": understanding_plots,
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

    # Get default configuration
    config = get_default_config()
    
    # Load required data
    gene_metadata, insertion_level, gene_level = load_depletion_data(config)

    long_timecourse_config = get_long_timecourse_config()
    _, insertion_level_long_timecourse, gene_level_long_timecourse = load_depletion_data(long_timecourse_config)
    
    haploid_config = get_haploid_config()
    _, insertion_level_haploid, gene_level_haploid = load_depletion_data(haploid_config)
    
    # Get gene input from sidebar
    covered_gene_sysIDs, submit_button = sidebar_gene_input(
        gene_metadata.gene_info_with_essentiality, 
        gene_level.gene_level_LFCs
    )

    if submit_button and covered_gene_sysIDs:
        for gene in covered_gene_sysIDs:
            with st.container(border=True):
                gene_info = get_gene_info(gene, gene_metadata.gene_info_with_essentiality)
                display_basic_information(gene, gene_info)
                
                gene_body = get_gene_body(gene, gene_metadata.genome_intervals)
                gene_length, gene_body_plot = display_gene_body(gene_body) 

                gene_level_fitting_results_in_current_gene, combined_plot, has_data = get_gene_result(
                    gene, 
                    gene_length, 
                    TIME_POINTS,
                    insertion_level, 
                    gene_level, 
                    gene_body_plot
                )

                gene_level_fitting_results_in_current_gene_long_timecourse, combined_plot_long_timecourse, has_data_long_timecourse = get_gene_result(
                    gene, 
                    gene_length, 
                    TIME_POINTS_LONG_TIMECOURSE,
                    insertion_level_long_timecourse, 
                    gene_level_long_timecourse, 
                    gene_body_plot
                )

                gene_level_fitting_results_in_current_gene_haploid, combined_plot_haploid, has_data_haploid = get_gene_result(
                    gene, 
                    gene_length, 
                    TIME_POINTS_HAPLOID,
                    insertion_level_haploid, 
                    gene_level_haploid, 
                    gene_body_plot
                )
                
                col1, col2, col3 = st.columns([1,1,1], border=True)
                if has_data:
                    with col1:
                        metrics = st.container(border=True)
                        display_gene_level_metrics(metrics, gene_level_fitting_results_in_current_gene)
                        chart = st.container(border=True)
                        with chart:
                            st.altair_chart(combined_plot, width="stretch", theme=None)
                else:
                    with col1:
                        st.warning("⚠️ No data found")
                if has_data_long_timecourse:
                    with col2:
                        metrics = st.container(border=True)
                        display_gene_level_metrics(metrics, gene_level_fitting_results_in_current_gene_long_timecourse)
                        chart = st.container(border=True)
                        with chart:
                            st.altair_chart(combined_plot_long_timecourse, width="stretch", theme=None)
                else:
                    with col2:
                        st.warning("⚠️ No data found")
                if has_data_haploid:
                    with col3:
                        metrics = st.container(border=True)
                        display_gene_level_metrics(metrics, gene_level_fitting_results_in_current_gene_haploid)
                        chart = st.container(border=True)
                        with chart:
                            st.altair_chart(combined_plot_haploid, width="stretch", theme=None)
                else:
                    with col3:
                        st.warning("⚠️ No data found")

                st.success("Plot generated successfully")
    else:
        st.warning("No genes submitted or no valid genes")


if __name__ == "__main__":
    main()