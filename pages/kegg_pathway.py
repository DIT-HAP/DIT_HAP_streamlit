# ================================= Imports =================================
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from kegg_pathway_functions import (
    load_all_kegg_pathways,
    convert_cx2_file_to_cytoscape_elements,
    node_color_mapping_panel,
    layout_algorithm_panel,
    get_stylesheet,
    display_kegg_network,
    display_selected_object,
)

# ================================= Page Config ====================================
st.set_page_config(
    page_title="KEGG Pathway Visualization",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# ================================ Configs =================================
KEGG_DATA_DIR = Path(__file__).parent.parent / "data" / "resource" / "kegg_pathways"

# =============================== Functions ================================
def display_pathway_information(
    kegg_pathways: dict,
) -> dict:
    st.header("Pathway Information", divider="gray")
    selected_pathway_title = str(st.selectbox("Select a KEGG Pathway", list(kegg_pathways.keys())))
    selected_pathway = kegg_pathways[selected_pathway_title]

    pathway_id = selected_pathway.get("KEGG_PATHWAY_ID", "N/A")
    classes = "\n\n".join(selected_pathway.get("classes", []))
    pathway_link = selected_pathway.get("KEGG_PATHWAY_LINK", "#")


    # Display pathway information
    col1, col2, col3 = st.columns(3)
    col1.markdown(f":material/barcode_scanner: **Pathway ID**\n\n{pathway_id}")
    col2.markdown(f":material/category: **Class**\n\n{classes if classes else 'N/A'}")
    col3.markdown(f":material/link: **KEGG Link**\n\n[View on KEGG]({pathway_link})")

    return selected_pathway

# ================================ Page Code ================================
def main():
    st.title(":material/account_tree: KEGG Pathway Visualization")

    # Introduction and Usage Guide
    st.markdown("""
    ### 🧪 KEGG Pathway Visualization

    This page provides **interactive network visualization of KEGG pathways** for understanding **molecular interactions** and **biological pathways** in cellular processes. KEGG (Kyoto Encyclopedia of Genes and Genomes) represents molecular interactions, reactions, and relation networks through pathway maps.
    """)

    with st.expander("📖 How to Use This Tool", expanded=False):
        st.markdown("""
        **Step 1: Select a KEGG Pathway**
        - Browse available pathways from the curated collection
        - View pathway metadata including name and file information
        - Choose pathways based on your biological interests
        - Pathways are organized by biological process and function

        **Step 2: Customize Network Display**
        - Adjust node colors based on biological features (viability, cluster, etc.)
        - Configure border styles and labels for better visual clarity
        - Apply different visual styles based on node characteristics
        - Network layout preserves original KEGG pathway structure

        **Step 3: Explore Pathway Interactions**
        - Click on nodes to view detailed biological information
        - Hover over edges to understand reaction types and relationships
        - Zoom and pan for detailed examination of complex pathways
        - Use edge labels to understand reaction mechanisms

        **Step 4: Analyze Biological Pathways**
        - Identify key enzymes and regulatory nodes
        - Trace metabolic pathways from substrates to products
        - Discover pathway connections and crosstalk
        - Compare different pathway structures across biological processes
        """)

    with st.expander("🔬 Understanding KEGG Pathways", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
                **🧬 What is KEGG?**

                **Kyoto Encyclopedia of Genes and Genomes** is a collection of databases depicting:
                - **Molecular pathways**: Metabolic and regulatory pathways
                - **Chemical compounds**: Metabolites and small molecules
                - **Enzymatic reactions**: Biochemical transformations
                - **Gene networks**: Regulatory and signaling networks
                - **Disease connections**: Pathological mechanisms

                **Network Components:**
                - **Nodes**: Enzymes, compounds, and genes
                - **Edges**: Reactions and regulatory relationships
                - **Shapes**: Different molecular types (enzymes, compounds, etc.)
                - **Colors**: Functional categories and pathways
                - **Labels**: Gene names and compound identifiers

                **Advantages:**
                - **Curated knowledge**: Expert-validated pathway information
                - **Standardized format**: Consistent representation across species
                - **Comprehensive coverage**: Multiple organism databases
                - **Integration**: Links to genes, compounds, and diseases
                """)

        with col2:
            st.markdown("""
                **📊 Pathway Visualizations**

                **Node Representations:**
                - **Rectangles**: Enzymes and gene products
                - **Circles**: Small molecules and compounds
                - **Rounded rectangles**: Complexes and multi-protein assemblies
                - **Color**: Functional categories or pathway membership
                - **Size**: Importance or abundance in the pathway

                **Edge Types:**
                - **Solid arrows**: Direct reactions (activation, conversion)
                - **Dashed lines**: Indirect effects or associations
                - **T-headed arrows**: Inhibition or repression
                - **Triangle arrows**: Activation or promotion
                - **Diamond arrows**: Binding/association

                **Pathway Layouts:**
                - **Original KEGG**: Preserves curated pathway structure
                - **Force-directed**: Auto-optimized node spacing
                - **Hierarchical**: Shows flow from upstream to downstream
                """)

    with st.expander("🎯 Analysis Applications", expanded=False):
        st.markdown("""
        **📈 Metabolic Research**
        - **Pathway reconstruction**: Build complete metabolic models from genomic data
        - **Flux analysis**: Understand metabolic flow and regulation
        - **Enzyme discovery**: Identify key enzymes in metabolic pathways
        - **Comparative metabolism**: Compare pathways across different species

        **🧪 Experimental Design**
        - **Hypothesis generation**: Predict metabolic consequences of genetic changes
        - **Target validation**: Assess essentiality of metabolic enzymes
        - **Biomarker discovery**: Identify pathway intermediates as markers
        - **Mechanism elucidation**: Understand how mutations affect metabolism

        **💊 Drug Discovery**
        - **Target identification**: Find enzymes for therapeutic intervention
        - **Mechanism of action**: Model drug effects on metabolic pathways
        - **Side effect prediction**: Anticipate off-target effects through pathway connections
        - **Combination therapy**: Design synergistic drug combinations based on pathway analysis

        **🔬 Disease Research**
        - **Disease mechanisms**: Model how genetic mutations cause metabolic disorders
        - **Genotype-phenotype mapping**: Connect molecular defects to cellular phenotypes
        - **Biomarker identification**: Find diagnostic markers for disease states
        - **Therapeutic strategies**: Design interventions based on pathway understanding
        """)

    with st.expander("⚙️ Technical Details", expanded=False):
        st.markdown("""
        **🔧 Data Format**
        - **CX2 format**: Standardized Cytoscape Network Exchange format
        - **KEGG KGML**: Original KEGG Markup Language representation
        - **Pathway coordinates**: Preserves original KEGG visual layout
        - **Node attributes**: Gene identifiers, compound names, enzyme classes
        - **Edge attributes**: Reaction types, stoichiometry, regulation

        **📊 Visualization Technology**
        - **Cytoscape.js**: Interactive network rendering in web browsers
        - **CX2 integration**: Direct KEGG to Cytoscape conversion
        - **Responsive design**: Works on desktop and mobile devices
        - **Performance optimization**: Efficient rendering of large pathways
        - **Custom styling**: Flexible visual appearance and layout options

        **🗂️ Data Management**
        - **Pathway repository**: Centralized collection of KEGG CX2 files
        - **Automatic loading**: Efficient parsing and indexing of pathway files
        - **Caching**: Fast repeated access to frequently used pathways
        - **Error handling**: Robust processing of incomplete or corrupted files
        - **Metadata tracking**: Pathway provenance and curation status

        **🔌 Integration with DIT-HAP Pipeline**
        - **Gene essentiality**: Connect essential genes to their metabolic functions
        - **Pathway mapping**: Visualize how essential genes fit into metabolic pathways
        - **Phenotype understanding**: Model how gene disruptions affect cellular metabolism
        - **Cross-species analysis**: Compare *S. pombe* pathways with other model organisms
        """)

    with st.expander("🔗 Integration with Other Analyses", expanded=False):
        st.markdown("""
        **🧬 Depletion Analysis Integration**
        - **Gene essentiality**: Connect essential genes from depletion curves to metabolic functions
        - **Pathway mapping**: Visualize how essential genes fit into complete metabolic pathways
        - **Mechanistic insight**: Understand why certain genes are essential for cell survival
        - **Compensation analysis**: Identify redundant pathways that can mask essentiality

        **📊 Feature Space Analysis Integration**
        - **Cluster interpretation**: Explain gene clusters in terms of shared metabolic pathways
        - **Pattern analysis**: Correlate statistical profiles with pathway membership
        - **Network motifs**: Identify recurring sub-network patterns in different gene sets
        - **Systems properties**: Analyze how gene clusters affect overall pathway behavior

        **🔍 Enrichment Analysis Integration**
        - **Mechanistic context**: Provide pathway explanations for enriched GO terms
        - **Network-based enrichment**: Identify over-represented pathway patterns and motifs
        - **Cross-validation**: Confirm enrichment results with pathway topology analysis
        - **Functional prediction**: Predict functions for uncharacterized genes based on pathway connections

        **🧫 Translational Research**
        - **Drug target validation**: Assess therapeutic potential of essential metabolic genes
        - **Disease gene mapping**: Connect *S. pombe* genes to human disease mechanisms
        - **Conserved pathways**: Identify evolutionarily conserved metabolic processes
        - **Mechanism-based therapy**: Design treatments based on pathway understanding
        """)

    with st.expander("💡 Analysis Tips", expanded=False):
        st.markdown("""
        **🔍 Pathway Selection**
        - **Start with central pathways**: Choose well-studied pathways like glycolysis or TCA cycle
        - **Match biological interests**: Select pathways relevant to your research questions
        - **Check file availability**: Ensure CX2 files are present in the data directory
        - **Review pathway documentation**: Look for pathway descriptions and supporting literature

        **🎨 Visual Customization**
        - **Color coding**: Use biologically meaningful colors (e.g., viability for essential genes)
        - **Label clarity**: Ensure gene names are readable at chosen zoom level
        - **Edge styling**: Differentiate between reaction types and regulatory relationships
        - **Layout optimization**: Try different layouts to best reveal pathway structure

        **🔬 Biological Interpretation**
        - **Follow metabolic chains**: Trace pathways from initial substrates to final products
        - **Identify control points**: Look for enzymes with many connections (hubs)
        - **Find regulatory loops**: Look for feedback regulation in metabolic pathways
        - **Assess pathway flux**: Consider directionality and reversibility of reactions

        **📈 Advanced Analysis**
        - **Compare multiple pathways**: Identify common network patterns across processes
        - **Pathway topology**: Analyze connectivity, branching, and pathway organization
        - **Flux simulation**: Consider how perturbations might affect pathway behavior
        - **Cross-reference with data**: Validate pathway connections with experimental evidence
        """)

    st.markdown("---")

    with st.spinner("Loading KEGG pathways..."):
        kegg_pathways = load_all_kegg_pathways(KEGG_DATA_DIR)

    with st.sidebar.expander(":material/brush: Node style settings", expanded=False):
        fill_feature, border_feature, label_feature = node_color_mapping_panel()

    with st.sidebar.expander(":material/dashboard: Layout settings", expanded=False):
        layout_type, _ = layout_algorithm_panel()

    network_col, detail_col = st.columns([2, 1], border=True)
    with detail_col:
        with st.expander(":material/left_click: Selected Object", expanded=True):
            pass  # Placeholder for selected object display

    with network_col:
        with st.container(border=True):
            selected_pathway = display_pathway_information(kegg_pathways)

        if selected_pathway:
            with st.spinner("Loading pathway network..."):
                cx2_data = selected_pathway.get("json", None)
                cytoscape_elements, elements_dict = convert_cx2_file_to_cytoscape_elements(cx2_data)

            if cytoscape_elements:
                custom_stylesheet, positions = get_stylesheet(
                    cytoscape_elements,
                    fill_feature,
                    border_feature,
                    label_feature
                )
            else:
                custom_stylesheet, positions = get_stylesheet()

            with st.container(border=True):
                network_tab, image_tab = st.tabs([":material/device_hub: KEGG Pathway Network", ":material/image: Pathway Image"])

                with network_tab:
                    st.markdown(f"<h2 style='text-align: center;'>{selected_pathway.get('name', 'Unknown Pathway')}</h2>", unsafe_allow_html=True)
                    selected_objects = display_kegg_network(
                        cytoscape_elements,
                        stylesheet=custom_stylesheet,
                        positions=positions,
                        layout_type=layout_type
                    )
                with image_tab:
                    st.markdown(f"<h2 style='text-align: center;'>{selected_pathway.get('name', 'Unknown Pathway')}</h2>", unsafe_allow_html=True)
                    st.image(selected_pathway["KEGG_PATHWAY_IMAGE"], caption="KEGG Pathway Image", width="stretch")

            with detail_col:
                with st.expander(":material/left_click: Selected Object", expanded=True):
                    display_selected_object(selected_objects, elements_dict)
        else:
            st.warning("No pathway selected.")
            cytoscape_elements = []
            elements_dict = {}


if __name__ == "__main__":
    main()
