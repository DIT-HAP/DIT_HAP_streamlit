# ================================= Imports =================================
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from go_cam_functions import (
    parse_gocam_model,
    convert_model_to_cytoscape_elements,
    load_all_gocam_models,
    plot_interaction_type_legend,
    display_gocam_network,
    display_selected_object,
    node_color_mapping_panel,
    apply_color_mapping_to_styles,
    layout_selection_panel,
    STYLE_SHEET
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
def display_model_information(
    gocam_models: dict,
) -> tuple[str, dict]:
    st.header("Model Information", divider="gray")
    selected_model_title = str(st.selectbox("Select a GO-CAM Model", list(gocam_models.keys())))
    selected_model = gocam_models[selected_model_title]["model"]
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

    with st.expander("📖 How to Use This Tool", expanded=False):
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

    with st.expander("🔬 Understanding GO-CAM", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
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
                """)

        with col2:
            st.markdown("""
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

                **Network Layouts:**
                - **Hierarchical**: Shows causal flow from upstream to downstream
                - **Circular**: Emphasizes feedback loops and cycles
                - **Force-directed**: Balances node spacing for readability
                - **Biologically-informed**: Incorporates known subcellular organization
                """)

    with st.expander("🎯 Analysis Applications", expanded=False):
        st.markdown("""
        **📈 Systems Biology Research**
        - **Pathway reconstruction**: Build complete mechanistic models from experimental data
        - **Predictive modeling**: Simulate effects of genetic perturbations or drug treatments
        - **Network analysis**: Identify bottlenecks, control points, and system robustness
        - **Comparative genomics**: Compare mechanisms across different species or conditions

        **🧪 Experimental Design**
        - **Hypothesis generation**: Predict outcomes of genetic interventions
        - **Target validation**: Assess essentiality and therapeutic potential
        - **Biomarker discovery**: Identify key regulatory molecules for monitoring
        - **Mechanism elucidation**: Understand how drugs or mutations affect cellular processes

        **💊 Drug Discovery**
        - **Target identification**: Find critical nodes for therapeutic intervention
        - **Mechanism of action**: Model how drugs affect biological networks
        - **Side effect prediction**: Anticipate off-target effects through network connections
        - **Combination therapy**: Design synergistic drug combinations based on pathway analysis

        **🔬 Disease Research**
        - **Disease mechanisms**: Model how genetic mutations cause pathological changes
        - **Genotype-phenotype mapping**: Connect molecular defects to cellular phenotypes
        - **Biomarker identification**: Find diagnostic markers for disease states
        - **Therapeutic strategies**: Design interventions based on mechanistic understanding
        """)

    with st.expander("⚙️ Technical Details", expanded=False):
        st.markdown("""
        **🔧 Model Structure**
        - **Data format**: Standardized GO-CAM format with RDF and OWL support
        - **Ontology integration**: Uses Gene Ontology terms and relationships
        - **Evidence codes**: Links to experimental support and literature
        - **Version control**: Track model evolution and provenance
        - **Quality assurance**: Curated by domain experts and automated validation

        **📊 Visualization Technology**
        - **Cytoscape.js**: Interactive network rendering in web browsers
        - **NDEx integration**: Network Data Exchange for model sharing
        - **Responsive design**: Works on desktop and mobile devices
        - **Performance optimization**: Efficient rendering of large networks
        - **Custom styling**: Flexible visual appearance and layout options

        **🗂️ Data Management**
        - **Model repository**: Centralized collection of curated GO-CAM models
        - **Automatic loading**: Efficient parsing and indexing of model files
        - **Caching**: Fast repeated access to frequently used models
        - **Error handling**: Robust processing of incomplete or corrupted models
        - **Metadata tracking**: Model provenance, creation dates, and curation status

        **🔌 Integration with DIT-HAP Pipeline**
        - **Gene function prediction**: Use GO-CAM to interpret essential genes identified in pipeline
        - **Pathway analysis**: Connect depleted genes to complete biological mechanisms
        - **Phenotype understanding**: Model how gene disruptions affect cellular processes
        - **Cross-species analysis**: Compare *S. pombe* mechanisms with other model organisms
        """)

    with st.expander("🔗 Integration with Other Analyses", expanded=False):
        st.markdown("""
        **🧬 Depletion Analysis Integration**
        - **Gene essentiality**: Connect essential genes from depletion curves to their molecular functions
        - **Pathway mapping**: Visualize how essential genes fit into complete biological pathways
        - **Mechanistic insight**: Understand why certain genes are essential for cell survival
        - **Compensation analysis**: Identify redundant pathways that can mask essentiality

        **📊 Feature Space Analysis Integration**
        - **Cluster interpretation**: Explain gene clusters in terms of shared molecular mechanisms
        - **Pattern analysis**: Correlate statistical profiles with network positions
        - **Network motifs**: Identify recurring sub-network patterns in different gene sets
        - **Systems properties**: Analyze how gene clusters affect overall network behavior

        **🔍 Enrichment Analysis Integration**
        - **Mechanistic context**: Provide causal explanations for enriched GO terms
        - **Network-based enrichment**: Identify over-represented network patterns and motifs
        - **Cross-validation**: Confirm enrichment results with network topology analysis
        - **Functional prediction**: Predict functions for uncharacterized genes based on network connections

        **🧫 Translational Research**
        - **Drug target validation**: Assess therapeutic potential of essential genes
        - **Disease gene mapping**: Connect *S. pombe* genes to human disease mechanisms
        - **Conserved pathways**: Identify evolutionarily conserved biological processes
        - **Mechanism-based therapy**: Design treatments based on mechanistic understanding
        """)

    with st.expander("💡 Analysis Tips", expanded=False):
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

        **📈 Advanced Analysis**
        - **Compare multiple models**: Identify common network patterns across processes
        - **Network topology**: Analyze connectivity, clustering, and centrality measures
        - **Pathway simulation**: Consider how perturbations might affect network behavior
        - **Cross-reference with data**: Validate model connections with experimental evidence
        """)

    st.markdown("---")

    with st.spinner("Loading GO-CAM models..."):
        gocam_models = load_all_gocam_models(GO_CAM_DATA_DIR)

    network_col, detail_col = st.columns([2, 1], border=True)
    with network_col:
        with st.container(border=True):
            selected_model_title, selected_model = display_model_information(gocam_models)
        
        if selected_model:
            cytoscape_elements, elements_dict = convert_model_to_cytoscape_elements(selected_model)
        else:
            st.warning("No model selected.")
            cytoscape_elements = []
            elements_dict = {}
        
        with st.sidebar.expander(":material/brush: Node style settings", expanded=False):
            if cytoscape_elements:
                fill_feature, border_feature, label_feature = node_color_mapping_panel(cytoscape_elements)
                custom_stylesheet = apply_color_mapping_to_styles(
                    STYLE_SHEET,
                    cytoscape_elements,
                    fill_feature,
                    border_feature,
                    label_feature
                )
            else:
                custom_stylesheet = STYLE_SHEET
        
        with st.sidebar.expander(":material/dashboard: Layout settings", expanded=False):
            selected_layout_config = layout_selection_panel()
        
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center;'>{gocam_models[selected_model_title]['title']}</h2>", unsafe_allow_html=True)
            selected_objects = display_gocam_network(
                cytoscape_elements, 
                layout_config=selected_layout_config,
                stylesheet=custom_stylesheet
            )

    with detail_col:
        with st.expander(":material/legend_toggle: Interaction Type Legend", expanded=True):
            plot_interaction_type_legend()
        with st.expander(":material/left_click: Selected Object", expanded=True):
            display_selected_object(selected_objects, elements_dict)

if __name__ == "__main__":
    main()