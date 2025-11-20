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
    display_selected_object
)
# ================================= Page Config ====================================
st.set_page_config(
    page_title="GO-CAM Model Visualization",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# ================================ Configs =================================
GO_CAM_DATA_DIR = Path(__file__).parent.parent / "data" / "resource" / "pombe_gocam"

# ================================ Page Code ================================
st.title("GO-CAM Model Visualization")

with st.spinner("Loading GO-CAM models..."):
    gocam_models = load_all_gocam_models(GO_CAM_DATA_DIR)

with st.container(border=True):
    st.header("Model Information")
    selected_model_title = st.selectbox("Select a GO-CAM Model", list(gocam_models.keys()))
    selected_model = gocam_models[selected_model_title]["model"]
    st.markdown(f"**Model ID:** {gocam_models[selected_model_title]['id']}")
    st.markdown(f"**Title:** {gocam_models[selected_model_title]['title']}")
    st.markdown(f"**Status:** {gocam_models[selected_model_title]['status']}")
    st.markdown(f"**Date:** {gocam_models[selected_model_title]['date']}")



network_col, detail_col = st.columns([3, 1], border=True)
with network_col:
    if selected_model:
        cytoscape_elements, elements_dict = convert_model_to_cytoscape_elements(selected_model)
    else:
        st.warning("No model selected.")
        cytoscape_elements = []
    
    selected_objects = display_gocam_network(cytoscape_elements)

with detail_col:
    with st.expander("Selected Object", expanded=True):
        display_selected_object(selected_objects, elements_dict)
    with st.expander("Interaction Type Legend", expanded=True):
        plot_interaction_type_legend()