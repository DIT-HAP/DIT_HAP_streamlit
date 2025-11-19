# ================================= Imports =================================
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from go_cam_functions import parse_gocam_model, convert_model_to_cytoscape_elements, load_all_gocam_models, display_gocam_network

# ================================ Configs =================================
GO_CAM_DATA_DIR = Path(__file__).parent.parent / "data" / "resource" / "pombe_gocam"

# ================================ Page Code ================================
st.title("GO-CAM Model Visualization")

with st.spinner("Loading GO-CAM models..."):
    gocam_models = load_all_gocam_models(GO_CAM_DATA_DIR)

with st.container(border=True):
    st.header("Model Info")
    selected_model_title = st.selectbox("Select a GO-CAM Model", list(gocam_models.keys()))
    selected_model = gocam_models[selected_model_title]["model"]
    st.markdown(f"**Model ID:** {gocam_models[selected_model_title]['id']}")
    st.markdown(f"**Title:** {gocam_models[selected_model_title]['title']}")
    st.markdown(f"**Status:** {gocam_models[selected_model_title]['status']}")
    st.markdown(f"**Date:** {gocam_models[selected_model_title]['date']}")

interaction_col, network_col = st.columns([1, 3], border=True)
with network_col:
    if selected_model:
        cytoscape_elements = convert_model_to_cytoscape_elements(selected_model)
    else:
        st.warning("No model selected.")
        cytoscape_elements = []

    display_gocam_network(cytoscape_elements)

with interaction_col:
    st.header("Interactions")
    if cytoscape_elements:
        edge_elements = [el for el in cytoscape_elements if 'source' in el['data']]
        for edge in edge_elements:
            st.markdown(f"**{edge['data']['source']}** -- *{edge['data']['interaction']}* --> **{edge['data']['target']}**")
    else:
        st.info("No interactions to display.")