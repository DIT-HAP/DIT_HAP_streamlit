# %% ================================= Imports =================================
import streamlit as st
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json
from typing import Any

from st_cytoscape import cytoscape

# for development in Jupyter Notebook
from streamlit_jupyter import StreamlitPatcher, tqdm
StreamlitPatcher().jupyter()

# %% ============================ Functions ============================
# ================================ Simple Functions =================================
# File extension to pandas reader mapping
_FILE_READERS = {
    '.tsv': lambda f: pd.read_csv(f, index_col=1, sep='\t'),
    '.csv': lambda f: pd.read_csv(f, index_col=1),
    '.xlsx': lambda f: pd.read_excel(f, index_col=1),
}

# ================================ Constants =================================
# -------------------------------- Data File Paths --------------------------------
GENE_LEVEL_DATA_FILE = Path('../data/raw/HD_DIT_HAP/gene_level/kmeans_cluster_result.tsv')

# -------------------------------- Default Colors --------------------------------
# Default color for missing/null values
_DEFAULT_COLOR = '#CCCCCC'

def get_theme_aware_label_color() -> str:
    """Get appropriate label color based on Streamlit theme."""
    try:
        return "#FFFFFF" if st.context.theme.type == "dark" else "#000000"
    except Exception:
        return "#000000"

THEME_COLOR = get_theme_aware_label_color()


# -------------------------------- Layout Configuration --------------------------------
LAYOUT_CONFIG = {
    "name": "dagre",
    "description": "Directed acyclic graph layout",
    "config": {
        "name": "dagre",
        "rankDir": "TB",
        "align": "DR",
        "fit": True,
        "nodeDimensionsIncludeLabels": True,
        # "ranker": "network-simplex",
        "acyclicer": "greedy",
        "padding": 10,
        "nodeSep": 50,
        "edgeSep": 70,
        "rankSep": 200,
        "spacingFactor": 1.2
    }
}

KLAY_LAYOUT_CONFIG = {
    "name": "klay",
    "fit": True,
    "padding": 10,
    "nodeDimensionsIncludeLabels": True,
    "klay": {
        "direction": "DOWN",
        "edgeSpacingFactor": 1.5,
        "inLayerSpacingFactor": 1,
        "aspectRatio": 0.1,
        "borderSpacing": 30,
        "spacing": 30
    }
}

# -------------------------------- Additional Metrics Configuration --------------------------------
ADDTIONAL_METRICS_VISUALIZATION = {
    "FYPOviability": {
        "range": ["inviable", "condition-dependent", "viable", "unknown"],
        "type": "categorical",
        "color_map": {
            "inviable": "#FF0000",  # Red for inviable
            "condition-dependent": "#FFA500",  # Orange for condition-dependent
            "viable": "#00FF00",  # Green for viable
            "unknown": "#CCCCCC"  # Gray for unknown
        }
    },
    "RevisedDeletion_essentiality": {
        "range": ["E", "V", "Not_determined"],
        "type": "categorical",
        "color_map": {
            "E": "#FF0000",  # Red for E/inviable
            "V": "#00FF00",  # Green for V/viable
            "Not_determined": "#CCCCCC"  # Gray for unknown
        }
    },
    "um": {
        "range": (-0.3, 1.5),
        "type": "numerical",
        "colormap": [
            mcolors.LinearSegmentedColormap.from_list("bwr", ["#0000FF", "#FFFFFF", "#FF0000"]),
            mcolors.TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5)
        ]
    },
    "lam": {
        "range": (0, 13),
        "type": "numerical",
        "colormap": [
            mcolors.LinearSegmentedColormap.from_list("reds", ["#FFFFFF", "#FF0000"]),
            mcolors.Normalize(vmin=0, vmax=13)
        ]
    },
    "revised_cluster": {
        "range": None,
        "type": "categorical",
        "color_map": {
            "default": "#CCCCCC"  # Gray for others
        }
    }
}

ADDITIONAL_METRICS = list(ADDTIONAL_METRICS_VISUALIZATION.keys())
MEMBER_METRICS = ["member_" + metric for metric in ADDITIONAL_METRICS]

# @st.cache_data
def prepare_additional_attributes(gene_level_data_file: Path) -> dict[str, dict[str, Any]]:
    """Load gene-level data and extract metrics as lookup dictionaries."""
    suffix = gene_level_data_file.suffix.lower()
    reader = _FILE_READERS.get(suffix)
    
    if not reader:
        raise ValueError(f"Unsupported file format: {suffix}. Use .tsv, .csv, or .xlsx")
    
    df = reader(gene_level_data_file)
    
    return {
        metric: df[metric].to_dict()
        for metric in ADDITIONAL_METRICS
        if metric in df.columns
    }

# ================================ CX2 to Cytoscape Conversion =================================
def _parse_kegg_cx2_node(node: dict, additional_attributes: dict) -> dict:
    """Parse a single CX2 node into Cytoscape element format."""
    node_id = str(node['id'])
    attrs = node.get('v', {})

    # 'id',
    # 'x',
    # 'y',
    # 'KEGG_NODE_X',
    # 'KEGG_NODE_Y',
    # 'KEGG_NODE_WIDTH',
    # 'KEGG_NODE_HEIGHT',
    # 'KEGG_LINK',
    # 'KEGG_NODE_LABEL_COLOR',
    # 'KEGG_NODE_SHAPE',
    # 'KEGG_NODE_FILL_COLOR',

    # 'name',
    # 'KEGG_ID',
    # 'KEGG_NODE_LABEL_LIST_FIRST',
    # 'KEGG_NODE_LABEL_LIST',
    # 'KEGG_NODE_LABEL',
    # 'KEGG_NODE_TYPE',
    # 'KEGG_NODE_REACTIONID',
    # 'KEGG_DEFINITION'

    # Build core attributes
    data = {
        "id": node_id,
        "label": attrs.get('KEGG_NODE_LABEL_LIST_FIRST', node_id).removeprefix("SPOM_"),
        "type": attrs.get('KEGG_NODE_TYPE', 'unknown'),
    }
    
    # Enrich with additional metrics (e.g., viability, cluster)
    for metric, lookup in additional_attributes.items():
        if data["label"] in lookup:
            data[metric] = lookup[data["label"]]

    # Copy remaining attributes (excluding already-handled keys)
    for key, value in attrs.items():
        if key not in data:
            data[key] = value
    
    return {"data": data}


def _parse_kegg_cx2_edge(edge: dict) -> dict:
    """Parse a single CX2 edge into Cytoscape element format."""
    edge_id = f"e{edge['id']}"
    attrs = edge.get('v', {})
    
    # Build core attributes
    data = {
        "id": edge_id,
        "source": str(edge['s']),
        "target": str(edge['t']),
        "interaction": attrs.get('interaction', ''),
    }
    
    # Copy remaining attributes (excluding already-handled keys)
    for key, value in attrs.items():
        if key not in data:
            data[key] = value
    
    return {"data": data}


def _parse_kegg_cx2_network(cx2_network: list, additional_attributes: dict) -> tuple[list, dict]:
    """Parse CX2 network fragments into Cytoscape elements."""
    elements = []
    elements_dict = {}
    
    for fragment in cx2_network:
        if 'nodes' in fragment:
            for node in fragment['nodes']:
                elem = _parse_kegg_cx2_node(node, additional_attributes)
                elements.append(elem)
                elements_dict[elem['data']['id']] = elem
        
        elif 'edges' in fragment:
            for edge in fragment['edges']:
                elem = _parse_kegg_cx2_edge(edge)
                elements.append(elem)
                elements_dict[elem['data']['id']] = elem
    
    return elements, elements_dict

# @st.cache_resource
def convert_cx2_file_to_cytoscape_elements(cx2_json: list) -> tuple[list, dict]:
    """Convert a cx2 file to Cytoscape elements."""
    
    # Step 3: Load additional gene-level attributes
    additional_attributes = prepare_additional_attributes(GENE_LEVEL_DATA_FILE)
    
    # Step 4: Parse into Cytoscape elements
    elements = _parse_kegg_cx2_network(cx2_json, additional_attributes)
    return elements


# %% =========================== Node Styles ============================
def _get_color_for_value(feature: str, value) -> str:
    """Map a feature value to a color.    
    - Categorical: lookup in color_map
    - Numerical: use colormap with normalization
    - Missing/None: return default gray
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return _DEFAULT_COLOR
    
    config = ADDTIONAL_METRICS_VISUALIZATION.get(feature)
    if not config:
        return _DEFAULT_COLOR
    
    if config["type"] == "categorical":
        color_map = config.get("color_map", {})
        return color_map.get(str(value), color_map.get("default", _DEFAULT_COLOR))
    
    # Numerical
    cmap, norm = config["colormap"]
    vmin, vmax = config["range"]
    clamped = max(vmin, min(vmax, float(value)))
    return mcolors.rgb2hex(cmap(norm(clamped))[:3])

def get_node_styles(
    elements: list | None = None,
    fill_feature: str | None = None,
    border_feature: str | None = None,
    label_feature: str | None = None,
) -> list:
    """Generate node styles, optionally with feature-based color mappings."""
    label_color = THEME_COLOR
    styles = []
    positions = {}

    # 1. Generate base styles for each node type
    for element in elements:
        element_data = element.get("data", {})
        node_id = element_data.get("id")
        style = {
            "label": "data(label)",
            "text-valign": "center",
            "text-halign": "left",
            "shape": element_data.get("KEGG_NODE_SHAPE", "ellipse").lower(),
            "background-color": element_data.get("KEGG_NODE_FILL_COLOR", "#FFFFFF"),
            "color": element_data.get("KEGG_NODE_LABEL_COLOR", label_color),
            "width": element_data.get("KEGG_NODE_WIDTH", 40),
            "height": element_data.get("KEGG_NODE_HEIGHT", 40),
        }
        styles.append({"selector": f"node[id='{node_id}']", "style": style})

        positions[node_id] = {
            "x": int(element_data.get("KEGG_NODE_X", 0)),
            "y": int(element_data.get("KEGG_NODE_Y", 0)),
        }
    
    # 2. Apply feature-based colors if elements provided
    if not elements:
        return styles
    
    # Collect active feature mappings
    feature_mappings = [
        (fill_feature, "background-color", {}),
        (border_feature, "border-color", {"border-width": 2}),
        (label_feature, "color", {}),
    ]
    active_mappings = [(f, prop, extra) for f, prop, extra in feature_mappings 
                       if f and f != "None"]
    
    if not active_mappings:
        return styles, positions
    
    # Generate per-node style overrides
    for elem in elements:
        data = elem.get("data", {})
        if "type" not in data:
            continue  # Skip edges
        
        node_style = {}
        for feature, css_prop, extras in active_mappings:
            node_style[css_prop] = _get_color_for_value(feature, data.get(feature))
            node_style.update(extras)
        
        if node_style:
            styles.append({
                "selector": f"node[id='{data['id']}']",
                "style": node_style,
            })
    
    return styles, positions

EDGE_STYLES = [  
    {  
        "selector": "edge",  
        "style": {  
            "width": 1.0,  
            "line-color": "#404040",  
            "line-style": "solid",  
            "opacity": 0.7058823529411765,  
            "curve-style": "bezier",  
            "target-arrow-shape": "none",  
            "target-arrow-color": "#404040",  
            "target-arrow-size": 6.0,  
            "source-arrow-shape": "none",  
            "source-arrow-color": "#404040",  
            "source-arrow-size": 6.0,  
            "label": "data(KEGG_EDGE_LABEL)",  
            "label-color": "#DC143C",  
            "label-opacity": 1.0,  
            "label-font-size": 10,  
            "label-font-family": "sans-serif",  
            "label-font-weight": "normal",  
            "label-font-style": "normal",  
            "text-rotation": 0.0,  
            "text-margin-x": 0.0,  
            "text-margin-y": 0.0,  
            "text-background-color": "#B6B6B6",  
            "text-background-opacity": 1.0,  
            "text-background-shape": "none",  
            "text-max-width": 200.0,  
            "text-valign": "center",  
            "text-halign": "center"  
        }  
    },  
    {  
        "selector": "edge:selected",  
        "style": {  
            "line-color": "#FF0000",  
            "target-arrow-color": "#FFFF00",  
            "source-arrow-color": "#FFFF00"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'expression']",  
        "style": {  
            "target-arrow-shape": "triangle"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'indirect effect']",  
        "style": {  
            "target-arrow-shape": "triangle-backcurve",  
            "line-style": "dashed"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'irreversible']",  
        "style": {  
            "target-arrow-shape": "triangle"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'inhibition']",  
        "style": {  
            "target-arrow-shape": "tee"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'repression']",  
        "style": {  
            "target-arrow-shape": "tee"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'activation']",  
        "style": {  
            "target-arrow-shape": "triangle"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'state change']",  
        "style": {  
            "line-style": "dotted"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'binding/association']",  
        "style": {  
            "line-style": "dashed"  
        }  
    },  
    {  
        "selector": "edge[KEGG_EDGE_SUBTYPES = 'maplink']",  
        "style": {  
            "line-style": "dashed"  
        }  
    }  
]
# %% ============================ Test Codes ============================
Gene_meta = pd.read_csv("../data/raw/HD_DIT_HAP/gene_level/kmeans_cluster_result.tsv", sep="\t", index_col=1)


cx2_folder = Path("../data/resource/kegg_pathways")
cx2_files = list(cx2_folder.glob("*.cx2"))

# load cx2 using json
with open(cx2_files[0], 'r') as f:
    cx2_json = json.load(f)



elements, elements_dict = convert_cx2_file_to_cytoscape_elements(cx2_json)

node_styles, positions = get_node_styles(elements)

style_sheet = node_styles + EDGE_STYLES

selected = cytoscape(
    elements,
    style_sheet,
    key="graph",
    layout={
        "name": "preset",
        "positions": positions,
        "fit": True,
        "padding": 4
    },
    min_zoom=0.2,
    max_zoom=3,
    user_panning_enabled=True,
    height="1500px",
    selection_type="single",
)
# %%
