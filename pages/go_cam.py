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
        
        with st.expander(":material/brush: Node style settings", expanded=False):
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
        
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center;'>{gocam_models[selected_model_title]['title']}</h2>", unsafe_allow_html=True)
            selected_objects = display_gocam_network(cytoscape_elements, stylesheet=custom_stylesheet)

    with detail_col:
        with st.expander(":material/legend_toggle: Interaction Type Legend", expanded=True):
            plot_interaction_type_legend()
        with st.expander(":material/left_click: Selected Object", expanded=True):
            display_selected_object(selected_objects, elements_dict)

if __name__ == "__main__":
    main()