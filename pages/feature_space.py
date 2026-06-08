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
from src.preparation import sidebar_gene_group_input
from src.data_config import get_default_config
from src.data_manager import load_gene_metadata, load_gene_level_stats, GeneLevelData

# =============================== Constants ================================
TIME_POINTS = {
    "YES0": 0,
    "YES1": 2.352,
    "YES2": 5.588,
    "YES3": 9.104,
    "YES4": 12.480
}

gRNA_TIME_POINTS = {
    "M_G0Tet": 0,
    "M_YES1_Tet": 3.703,
    "M_YES2_Tet": 6.816,
    "M_YES3_Tet": 10.292,
    "M_YES4_Tet": 13.594,
    "M_YES5_Tet": 16.723
}

# ================================= Functions =================================

@st.dialog("❓ How to Use This Tool", width="large")
def how_to_use_this_tool():
    """Dialog explaining how to use the feature space visualization tool."""
    st.markdown("""
        **Step 1: Add Gene Groups** (Sidebar)
        - Enter a descriptive name for your gene group (e.g., "Essential genes", "DNA repair")
        - Input gene names (e.g., `cdc2`, `wee1`) or systematic IDs (e.g., `SPAC1002.09c`)
        - Separate multiple genes with commas or newlines
        - Click "Add Group" to add the group to the visualization

        **Step 2: Add Multiple Groups**
        - Repeat Step 1 to add additional gene groups
        - Each group will be displayed with a different color
        - Groups are listed in the sidebar with their names and gene counts
        - You can add up to 8 groups with distinct colors (colors cycle after 8)

        **Step 3: Interpret the Plot**
        - **X-axis (Depletion rate)**: How quickly genes are depleted over time (μ parameter)
        - **Y-axis (Depletion lag)**: Time delay before depletion begins (λ parameter)
        - **Gray circles**: Background genes (all genes in the dataset)
        - **Colored circles**: Your gene groups (each group has a unique color)
        - **Legend**: Shows group names with corresponding colors

        **Step 4: Manage Groups**
        - View current groups in the sidebar
        - Click "Clear All" to remove all groups and start fresh
        - The plot updates automatically when groups are added or cleared
        """)

@st.dialog("🔬 Understanding Feature Space", width="large")
def understanding_feature_space():
    """Dialog explaining the feature space visualization."""
    st.markdown("""
        **What is Feature Space?**

        Feature space visualization places genes in a 2D plot based on their statistical properties from the DIT-HAP pipeline:
        - **Depletion rate (μ)**: The rate at which transposon insertions in a gene decrease over time
        - **Depletion lag (λ)**: The time delay before depletion begins

        **Interpreting the Plot:**
        - **Upper right**: High depletion rate, long lag → Genes that deplete quickly but after a delay
        - **Lower right**: High depletion rate, short lag → Rapidly depleting essential genes
        - **Upper left**: Low depletion rate, long lag → Slow depletion with delayed onset
        - **Lower left**: Low depletion rate, short lag → Non-essential genes with minimal depletion

        **Multi-Group Analysis:**
        - **Compare gene sets**: Add multiple groups to compare different gene categories
        - **Color-coded groups**: Each group has a distinct color for easy identification
        - **Legend**: Group names displayed in legend for reference
        - **Overlap detection**: See if genes from different groups cluster together

        **Biological Meaning:**
        - **Essential genes**: Higher depletion rates indicate negative fitness effects
        - **Non-essential genes**: Lower depletion rates suggest neutral fitness effects
        - **Condition-specific genes**: May show intermediate patterns depending on experimental conditions
        - **Pathway genes**: Genes in the same pathway may cluster in feature space
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
        - **Functional groups**: Group genes by GO terms or phenotype annotations

        **Multi-Group Comparison:**
        - **Compare pathways**: Add different pathway gene sets as separate groups
        - **Essential vs non-essential**: Create groups for known essential and non-essential genes
        - **Time course patterns**: Group genes by their depletion timing patterns
        - **Mutant comparisons**: Compare gene sets from different mutant backgrounds

        **Interpreting Patterns:**
        - **Tightly grouped genes**: Share similar depletion characteristics
        - **Scattered genes**: Diverse fitness effects within your gene set
        - **Overlap with background**: Query genes similar to population average
        - **Outliers**: May indicate unique biological properties or data quality issues
        - **Group overlap**: Different groups clustering together suggest shared biology

        **Comparative Analysis:**
        - Compare gene positions across different experimental conditions
        - Look for shifts in feature space indicating condition-specific effects
        - Use feature space to validate gene essentiality predictions
        - Cross-reference with enrichment analysis results
        - Identify genes that behave differently across groups
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

def get_group_color_palette() -> list[str]:
    """
    Get a color palette for gene groups.
    Uses a colorblind-friendly palette with 8 distinct colors.
    """
    return [
        "#e41a1c",  # Red
        "#377eb8",  # Blue
        "#4daf4a",  # Green
        "#984ea3",  # Purple
        "#ff7f00",  # Orange
        "#ffff33",  # Yellow
        "#a65628",  # Brown
        "#f781bf",  # Pink
    ]


def display_depletion_curves(gene_groups: list[dict], gene_level: GeneLevelData, gene_metadata, timepoints: dict) -> alt.Chart:
    """
    Display depletion curves for gene groups as line charts.
    
    Args:
        gene_groups: List of group dictionaries with "name", "genes", and "color" keys
        gene_level: GeneLevelData containing gene_level_LFCs with timepoint columns
        gene_metadata: GeneMetadataData containing id2name mapping
        timepoints: Dictionary mapping timepoint names to values (e.g., {"YES0": 0, "YES1": 2.352, ...})
    
    Returns:
        Altair chart with line plots for each gene group
    """
    # Get color palette
    color_palette = get_group_color_palette()
    
    # Get timepoint keys and values
    tp_keys = list(timepoints.keys())
    tp_values = list(timepoints.values())
    
    # Prepare data with gene names
    gene_level_lfcs = gene_level.gene_level_LFCs.copy()
    
    # Add gene name column using id2name mapping
    gene_level_lfcs["Gene Name"] = gene_level_lfcs.index.map(
        lambda x: gene_metadata.id2name.get(x, x)
    )
    
    # If no groups, return empty chart
    if not gene_groups:
        return alt.Chart(pd.DataFrame()).mark_point().encode(
            x=alt.X("x:Q", title="Generations"),
            y=alt.Y("y:Q", title="Log Fold Change")
        ).properties(title="No gene groups to display")
    
    # Prepare combined data for all groups
    all_groups_data = []
    group_names = []
    group_colors = []
    
    for idx, group in enumerate(gene_groups):
        group_name = group["name"]
        group_genes = group["genes"]
        # Use custom color if provided, otherwise use palette color
        group_color = group.get("color", color_palette[idx % len(color_palette)])
        
        # Filter data for this group
        group_data = gene_level_lfcs.loc[
            gene_level_lfcs.index.isin(group_genes)
        ].copy()
        
        # Transform wide format to long format for line plotting
        for gene_sys_id in group_data.index:
            gene_row = group_data.loc[gene_sys_id]
            gene_name = gene_row["Gene Name"]
            
            for tp_key in tp_keys:
                all_groups_data.append({
                    "Group": group_name,
                    "Gene Name": gene_name,
                    "Systematic ID": gene_sys_id,
                    "Generations": timepoints[tp_key],
                    "Timepoint": tp_key,
                    "LFC": gene_row[tp_key]
                })
        
        group_names.append(group_name)
        group_colors.append(group_color)
    
    # Create DataFrame from combined data
    combined_data = pd.DataFrame(all_groups_data)
    
    # Sort data by group and timepoint order (YES0 -> YES1 -> YES2 -> YES3 -> YES4)
    tp_order = {tp: idx for idx, tp in enumerate(tp_keys)}
    combined_data["tp_order"] = combined_data["Timepoint"].map(tp_order)
    combined_data = combined_data.sort_values(["Group", "Gene Name", "tp_order"]).drop(columns=["tp_order"])
    
    # Create line chart with points
    # Lines colored by group, with individual gene tooltips
    # Use detail to separate different genes within the same group
    line_chart = alt.Chart(combined_data).mark_line(
        opacity=0.7,
        point=True
    ).encode(
        x=alt.X("Generations:Q", title="Generations", 
                scale=alt.Scale(domain=(0, max(tp_values) + 1)),
                sort=tp_keys),
        y=alt.Y("LFC:Q", title="Log Fold Change",
                scale=alt.Scale(domain=(-3, 8))),
        color=alt.Color(
            "Group:N",
            scale=alt.Scale(
                domain=group_names,
                range=group_colors
            ),
            legend=alt.Legend(
                title="Gene Groups",
                orient="right",
                titleFontSize=14,
                labelFontSize=12
            )
        ),
        detail=alt.Detail("Systematic ID:N"),
        tooltip=[
            alt.Tooltip("Group:N", title="Group"),
            alt.Tooltip("Gene Name:N", title="Gene Name"),
            alt.Tooltip("Systematic ID:N", title="Systematic ID"),
            alt.Tooltip("Timepoint:N", title="Timepoint"),
            alt.Tooltip("Generations:Q", title="Generations", format=".3f"),
            alt.Tooltip("LFC:Q", title="LFC", format=".3f")
        ],
        order=alt.Order("Timepoint:O", sort="ascending")
    ).properties(
        width=700,
        height=500,
        title="Gene Depletion Curves by Group"
    )
    
    return line_chart


def get_group_color_palette() -> list[str]:
    """
    Get a color palette for gene groups.
    Uses a colorblind-friendly palette with 8 distinct colors.
    """
    return [
        "#e41a1c",  # Red
        "#377eb8",  # Blue
        "#4daf4a",  # Green
        "#984ea3",  # Purple
        "#ff7f00",  # Orange
        "#ffff33",  # Yellow
        "#a65628",  # Brown
        "#f781bf",  # Pink
    ]


def display_feature_space(gene_groups: list[dict], gene_level: GeneLevelData, gene_metadata) -> alt.Chart | alt.LayerChart:
    """
    Display the feature space with multiple gene groups.
    
    Args:
        gene_groups: List of group dictionaries with "name", "genes", and "color" keys
        gene_level: GeneLevelData containing fitting results with "um" and "lam" columns
        gene_metadata: GeneMetadataData containing id2name mapping
    
    Returns:
        Altair chart (single or layered) with background genes and colored gene groups
    """
    # Get color palette
    color_palette = get_group_color_palette()
    
    # Prepare data with gene names
    fitting_results = gene_level.gene_level_fitting_results.copy()
    
    # Add gene name column using id2name mapping
    fitting_results["Gene Name"] = fitting_results.index.map(
        lambda x: gene_metadata.id2name.get(x, x)
    )
    
    # Create background chart (all genes in light gray)
    background_chart = alt.Chart(fitting_results).mark_circle(
        opacity=0.4,
        size=80
    ).encode(
        x=alt.X("um:Q", title="Depletion rate (μ)"),
        y=alt.Y("lam:Q", title="Depletion lag (λ)"),
        color=alt.value("lightgray"),
        tooltip=[
            alt.Tooltip("Gene Name:N", title="Gene Name"),
            alt.Tooltip("index:N", title="Systematic ID"),
            alt.Tooltip("um:Q", title="Depletion rate (μ)", format=".3f"),
            alt.Tooltip("lam:Q", title="Depletion lag (λ)", format=".3f")
        ]
    ).properties(
        width=600,
        height=600
    )
    
    # If no groups, return just the background
    if not gene_groups:
        return background_chart
    
    # Prepare combined data for all groups with unified color mapping
    all_groups_data = []
    group_names = []
    group_colors = []
    
    for idx, group in enumerate(gene_groups):
        group_name = group["name"]
        group_genes = group["genes"]
        # Use custom color if provided, otherwise use palette color
        group_color = group.get("color", color_palette[idx % len(color_palette)])
        
        # Filter data for this group
        group_data = fitting_results.loc[
            fitting_results.index.isin(group_genes)
        ].copy()
        
        # Add group name column
        group_data["Group"] = group_name
        
        all_groups_data.append(group_data)
        group_names.append(group_name)
        group_colors.append(group_color)
    
    # Combine all group data
    combined_groups_data = pd.concat(all_groups_data, ignore_index=False)
    
    # Create overlay chart for all groups with unified color scale
    groups_chart = alt.Chart(combined_groups_data).mark_circle(
        opacity=0.8,
        size=100
    ).encode(
        x=alt.X("um:Q", title="Depletion rate (μ)"),
        y=alt.Y("lam:Q", title="Depletion lag (λ)"),
        color=alt.Color(
            "Group:N",
            scale=alt.Scale(
                domain=group_names,
                range=group_colors
            ),
            legend=alt.Legend(
                title="Gene Groups",
                orient="right",
                titleFontSize=20,
                labelFontSize=16
            )
        ),
        tooltip=[
            alt.Tooltip("Group:N", title="Group"),
            alt.Tooltip("Gene Name:N", title="Gene Name"),
            alt.Tooltip("index:N", title="Systematic ID"),
            alt.Tooltip("um:Q", title="Depletion rate (μ)", format=".3f"),
            alt.Tooltip("lam:Q", title="Depletion lag (λ)", format=".3f")
        ]
    ).properties(
        width=600,
        height=600
    )
    
    # Combine background and groups overlay
    return background_chart + groups_chart

def display_current_groups(gene_groups: list[dict]):
    """
    Display the current gene groups in the sidebar.
    
    Args:
        gene_groups: List of group dictionaries with "name", "genes", and "color" keys
    """
    if not gene_groups:
        st.sidebar.info("No gene groups added yet")
        return
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Current Groups")
    
    for group in gene_groups:
        # Use the group's actual color (from color picker)
        group_color = group.get("color", "#e41a1c")  # Default to red if no color
        group_name = group["name"]
        gene_count = len(group["genes"])
        
        # Create a colored badge for each group
        st.sidebar.markdown(
            f"<div style='display: flex; align-items: center; margin-bottom: 5px;'>"
            f"<div style='width: 20px; height: 20px; background-color: {group_color}; "
            f"border-radius: 50%; margin-right: 10px;'></div>"
            f"<span style='font-weight: 500;'>{group_name}</span>"
            f"<span style='color: gray; margin-left: 10px;'>({gene_count} genes)</span>"
            f"</div>",
            unsafe_allow_html=True
        )


def main():
    """Main entry point for the feature space page."""

    st.title(":chart_with_upwards_trend: Feature Space Visualization")

    # Introduction and Usage Guide
    st.markdown("""
    ### 📊 Multi-Dimensional Feature Space Analysis

    This page provides **interactive visualization of genes in feature space** based on statistical parameters from the **[DIT-HAP pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)**. Explore how your genes of interest compare to the genome-wide distribution.
    
    **Features:**
    - Add multiple gene groups with custom names
    - Each group displayed with distinct color and legend
    - Compare multiple gene sets simultaneously
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

    # Initialize session state for gene groups
    if "gene_groups" not in st.session_state:
        st.session_state.gene_groups = []
    
    # Load required data
    gene_metadata, gene_level = load_data()
    
    # Get background genes
    bg_genes = set(gene_level.gene_level_LFCs.index.tolist())
    
    # Get gene group input from sidebar
    group_data, add_clicked, clear_clicked = sidebar_gene_group_input(
        gene_metadata.gene_info_with_essentiality,
        gene_level.gene_level_LFCs,
        bg_genes,
        st.session_state.gene_groups
    )
    
    # Handle add button
    if add_clicked and group_data:
        st.session_state.gene_groups.append(group_data)
    
    # Handle clear button
    if clear_clicked:
        st.session_state.gene_groups = []
        # Reset group counter to 1 when clearing all groups
        if "group_counter" in st.session_state:
            st.session_state.group_counter = 1
        # Reset name and color to default
        if "current_group_name" in st.session_state:
            st.session_state.current_group_name = "Group 1"
        if "current_group_color" in st.session_state:
            st.session_state.current_group_color = "#e41a1c"  # First color in palette (red)
        st.sidebar.success("✅ All groups cleared")
    
    # Display current groups in sidebar
    display_current_groups(st.session_state.gene_groups)
    
    # Display feature space chart
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📈 Feature Space Plot (DR vs DL)")
        
        if st.session_state.gene_groups:
            st.markdown(f"**Displaying {len(st.session_state.gene_groups)} gene group(s)**")
        else:
            st.info("💡 Add gene groups using the sidebar to visualize them in feature space")
        
        # Create and display the feature space chart (use original aspect ratio, not full width)
        alt_chart = display_feature_space(st.session_state.gene_groups, gene_level, gene_metadata)
        st.altair_chart(alt_chart, width="content")
    
    with col2:
        # Display depletion curves
        st.subheader("📉 Depletion Curves by Group")
        
        if st.session_state.gene_groups:
            st.markdown(f"**Displaying depletion curves for {len(st.session_state.gene_groups)} gene group(s)**")
        else:
            st.info("💡 Add gene groups using the sidebar to visualize depletion curves")
        
        # Create and display the depletion curves chart
        depletion_chart = display_depletion_curves(st.session_state.gene_groups, gene_level, gene_metadata, TIME_POINTS)
        st.altair_chart(depletion_chart, width="content")

if __name__ == "__main__":
    main()