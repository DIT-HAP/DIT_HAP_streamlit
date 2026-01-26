# ================================= Imports =================================
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from src.network_functions import (
    load_all_gocam_models,
    convert_cx2_json_to_cytoscape_elements,
    node_color_mapping_panel,
    layout_algorithm_panel,
    get_layout_config,
    display_network,
    display_selected_object
)
from src.go_cam_functions import (
    get_stylesheet,
    plot_interaction_type_legend,
)
# ================================= Page Config ====================================
st.set_page_config(
    page_title="GO-CAM Model Visualization",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# ================================ Configs =================================
GO_CAM_DATA_DIR = Path(__file__).parent.parent / "data" / "resource" / "pombe_gocam"

# =============================== Constants ================================
MODEL_STATES = {
    "Production": ":green-badge[:material/check: Production]\n\nReady for public use",
    "Development": ":blue-badge[:material/build_circle: Development]\n\nWork in progress",
    "Review": ":yellow-badge[:material/grading: Review]\n\nMarked for curator review",
    "Delete": ":red-badge[:material/scan_delete: Delete]\n\nMarked for deletion"
}

# =============================== Functions ================================

@st.dialog("❓ How to Use This Tool", width="large")
def how_to_use_this_tool():
    """Dialog explaining how to use the GO-CAM visualization tool."""
    st.markdown("""
        **Step 1: Select a GO-CAM Model**
        - Browse available models from the curated collection
        - View model metadata including ID, status, and creation date
        - Choose models based on your biological interests
        - Model status indicates: Production (ready), Development (in progress), Review (curator review), Delete (marked for removal)

        **Step 2: Customize Network Display**
        - Adjust node colors based on biological features (molecular function, cellular component, etc.)
        - Configure border styles and labels for better visual clarity
        - Apply different visual styles based on model characteristics
        - Network layout automatically optimized for readability

        **Step 3: Explore Network Interactions**
        - Click on nodes to view detailed biological information
        - Hover over edges to understand interaction types
        - Use interaction type legend to decode relationship meanings
        - Zoom and pan for detailed examination of complex pathways

        **Step 4: Analyze Biological Mechanisms**
        - Identify key regulatory nodes and control points
        - Trace causal pathways from inputs to outputs
        - Discover feedback loops and network motifs
        - Compare different model structures across biological processes
        """)

@st.dialog("🔬 Understanding GO-CAM", width="large")
def understanding_gocam():
    """Dialog explaining GO-CAM network visualization."""
    st.markdown("""
        **🧬 What is GO-CAM?**

        **Gene Ontology Causal Activity Models** are directed networks that represent:
        - **Molecular activities**: Individual protein functions and biochemical processes
        - **Causal relationships**: How one molecular activity affects another
        - **Biological mechanisms**: Complete pathways from stimuli to responses
        - **Temporal ordering**: Sequence of molecular events in cellular processes

        **Network Components:**
        - **Nodes**: Individual molecular activities (GO terms)
        - **Edges**: Causal relationships between activities
        - **Properties**: Molecular features, cellular locations, regulatory information
        - **Annotations**: Evidence codes and supporting literature

        **Advantages over GO:**
        - **Causal directionality**: Beyond simple association to mechanistic understanding
        - **Dynamic modeling**: Can simulate temporal behavior and predict outcomes
        - **Mechanistic insight**: Reveals how biological processes actually work
        - **Computational prediction**: Supports reasoning about biological systems

        **📊 Network Visualizations**

        **Node Representations:**
        - **Shape**: Different molecular function categories
        - **Color**: Biological properties or cellular compartments
        - **Size**: Importance or activity level in the model
        - **Border**: Confidence level or evidence type
        - **Labels**: GO term names or systematic identifiers

        **Edge Types:**
        - **Direct regulation**: Immediate causal effects
        - **Indirect regulation**: Multi-step causal pathways
        - **Positive influence**: Activity activation or enhancement
        - **Negative influence**: Activity inhibition or suppression
        - **Bidirectional**: Complex regulatory relationships
        """)

@st.dialog("⚙️ Data Requirements", width="large")
def data_requirements():
    """Dialog explaining the data requirements for GO-CAM visualization."""
    st.markdown("""
        **Required Data:**
        - **GO-CAM model files**: Standardized format with RDF and OWL support
        - **Model repository**: Centralized collection of curated GO-CAM models
        - **Ontology integration**: Uses Gene Ontology terms and relationships
        - **Evidence codes**: Links to experimental support and literature

        **Model Structure:**
        - **Data format**: Standardized GO-CAM format with RDF and OWL support
        - **Ontology integration**: Uses Gene Ontology terms and relationships
        - **Evidence codes**: Links to experimental support and literature
        - **Version control**: Track model evolution and provenance
        - **Quality assurance**: Curated by domain experts and automated validation

        **Data Management:**
        - **Model repository**: Centralized collection of curated GO-CAM models
        - **Automatic loading**: Efficient parsing and indexing of model files
        - **Caching**: Fast repeated access to frequently used models
        - **Error handling**: Robust processing of incomplete or corrupted models
        - **Metadata tracking**: Model provenance, creation dates, and curation status
        """)

@st.dialog("🎯 Analysis Tips", width="large")
def analysis_tips():
    """Dialog providing analysis tips for GO-CAM network exploration."""
    st.markdown("""
        **🔍 Model Selection**
        - **Start with established models**: Choose well-curated models for learning the interface
        - **Match biological interests**: Select models relevant to your research questions
        - **Check status**: Prefer models marked as "Production" for highest quality
        - **Review documentation**: Look for model descriptions and supporting literature

        **🎨 Visual Customization**
        - **Color coding**: Use biologically meaningful colors (e.g., organelle-specific)
        - **Label clarity**: Ensure GO terms are readable at chosen zoom level
        - **Edge styling**: Differentiate between regulatory types and confidence levels
        - **Layout optimization**: Try different layouts to best reveal network structure

        **🔬 Biological Interpretation**
        - **Follow causal chains**: Trace pathways from initial stimuli to final outputs
        - **Identify control points**: Look for nodes with many outgoing connections
        - **Find feedback loops**: Look for cycles that regulate biological processes
        - **Assess evidence quality**: Pay attention to confidence levels and evidence types

        **🔌 Integration with DIT-HAP Pipeline**
        - **Gene function prediction**: Use GO-CAM to interpret essential genes identified in pipeline
        - **Pathway analysis**: Connect depleted genes to complete biological mechanisms
        - **Phenotype understanding**: Model how gene disruptions affect cellular processes
        - **Cross-species analysis**: Compare *S. pombe* mechanisms with other model organisms
        """)

# ================================ Page Code ================================
def display_model_information(
    gocam_models: dict,
) -> tuple[str, dict]:
    st.header("Model Information", divider="gray")
    selected_model_title = str(st.selectbox("Select a GO-CAM Model", list(gocam_models.keys())))
    selected_model = gocam_models[selected_model_title]
    col1, col2, col3 = st.columns(3)
    col1.markdown(f":material/barcode_scanner: **Model ID**\n\n{gocam_models[selected_model_title]['id']}")
    col2.markdown(f":material/fact_check: **Status** {MODEL_STATES.get(gocam_models[selected_model_title]['status'], gocam_models[selected_model_title]['status'])}")
    col3.markdown(f":material/calendar_month: **Date**\n\n{gocam_models[selected_model_title]['date']}")

    return selected_model_title, selected_model

# ================================ Page Code ================================
def main():
    st.title(":material/account_tree: GO-CAM Model Visualization")

    # Introduction and Usage Guide
    st.markdown("""
    ### 🕸️ Gene Ontology Causal Activity Model (GO-CAM) Visualization

    This page provides **interactive network visualization of GO-CAM models** for understanding **causal relationships** and **biological mechanisms** in cellular processes. GO-CAM represents molecular activities and their causal interactions through directed networks.
    """)

    usage_guides = {
        "❓ How to Use This Tool": how_to_use_this_tool,
        "🔬 Understanding GO-CAM": understanding_gocam,
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

    # with st.spinner("Loading GO-CAM models..."):
    with st.spinner():
        gocam_models = load_all_gocam_models(GO_CAM_DATA_DIR)
    
    with st.sidebar.expander(":material/brush: Node style settings", expanded=False):
        fill_feature, border_feature, label_feature = node_color_mapping_panel()
    
    with st.sidebar.expander(":material/dashboard: Layout settings", expanded=False):
        layout_type, ranker = layout_algorithm_panel()

    with st.sidebar.expander(":material/visibility_off: Show chemicals", expanded=False):
        show_chemicals = st.toggle("Show chemical nodes in the network", value=False)

    network_col, detail_col = st.columns([2, 1], border=True)
    with detail_col:
        with st.expander(":material/legend_toggle: Interaction Type Legend", expanded=True):
            plot_interaction_type_legend()


    with network_col:
        with st.container(border=True):
            selected_model_title, selected_model = display_model_information(gocam_models)
        
        if selected_model:
            with st.spinner("Converting model to network elements..."):
                cx2_data = selected_model.get('cx2_network', [])
                cytoscape_elements, elements_dict, positions = convert_cx2_json_to_cytoscape_elements(cx2_data, pathway_type="go-cam")
                layout_config = get_layout_config(positions, layout_type=layout_type, ranker=ranker)
            if cytoscape_elements:
                custom_stylesheet = get_stylesheet(
                    cytoscape_elements,
                    fill_feature,
                    border_feature,
                    label_feature
                )
            else:
                raise ValueError("No cytoscape elements generated from the selected model.")
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align: center;'>{gocam_models[selected_model_title]['title']}</h2>", unsafe_allow_html=True)
                selected_objects = display_network(
                    cytoscape_elements, 
                    stylesheet=custom_stylesheet,
                    layout_config=layout_config
                )
            with detail_col:
                with st.expander(":material/left_click: Selected Object", expanded=True):
                    display_selected_object(selected_objects, elements_dict)
        else:
            st.warning("No model selected.")
            cytoscape_elements = []
            elements_dict = {}
        
if __name__ == "__main__":
    main()