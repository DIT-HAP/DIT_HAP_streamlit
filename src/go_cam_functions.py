"""

"""
# %%
# ================================= Imports =================================
import streamlit as st
import yaml
from pathlib import Path

from gocam.datamodel import Model
from gocam.translation.cx2.main import model_to_cx2
from st_cytoscape import cytoscape


# ================================ Style Configuration =================================
NODE_STYLES = [
    {
        "selector": "node[type='gene']",
        "style": {
            "shape": "ellipse",
            "background-color": "#C8E6C9",
            "label": "data(label)"
        }
    },
    {
        "selector": "node[type='complex']",
        "style": {
            "shape": "rectangle",
            "background-color": "#E2BDE7",
            "label": "data(label)"
        }
    },
    {
        "selector": "node[type='molecule']",
        "style": {
            "shape": "rectangle",
            "background-color": "#B2DFDB",
            "label": "data(label)"
        }
    }
]

EDGE_STYLES = [
    {
        "selector": 'edge[interaction="directly positively regulates"]',
        "style": {
            "width": 3,
            "line-color": "#008800",
            "line-style": "solid",
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#008800",
        }
    },
    {
        "selector": 'edge[interaction="directly negatively regulates"]',
        "style": {
            "width": 3,
            "line-color": "#FF0000",
            "line-style": "solid",
            "curve-style": "bezier",
            "target-arrow-shape": "tee",
            "target-arrow-color": "#FF0000",
        }
    },
    {
        "selector": 'edge[interaction="indirectly positively regulates"]',
        "style": {
            "width": 3,
            "line-color": "#008800",
            "line-style": "dashed",
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#008800",
        }
    },
    {
        "selector": 'edge[interaction="indirectly negatively regulates"]',
        "style": {
            "width": 3,
            "line-color": "#FF0000",
            "line-style": "dashed",
            "curve-style": "bezier",
            "target-arrow-shape": "tee",
            "target-arrow-color": "#FF0000",
        }
    },
    {
        "selector": 'edge[interaction="provides input for"]',
        "style": {
            "width": 3,
            "line-color": "#800080",
            "line-style": "solid",
            "curve-style": "bezier",
            "target-arrow-shape": "diamond",
            "target-arrow-color": "#800080",
        }
    },
    {
        "selector": 'edge[interaction="removes input for"]',
        "style": {
            "width": 3,
            "line-color": "#FF9999",
            "line-style": "solid",
            "curve-style": "bezier",
            "target-arrow-shape": "square",
            "target-arrow-color": "#FF9999",
        }
    },
    {
        "selector": 'edge[interaction="has input"]',
        "style": {
            "width": 3,
            "line-color": "#6495ED",
            "line-style": "solid",
            "curve-style": "bezier",
            "target-arrow-shape": "none",
            "source-arrow-shape": "circle",
            "source-arrow-color": "#6495ED",
        }
    },
    {
        "selector": 'edge[interaction="has output"]',
        "style": {
            "width": 3,
            "line-color": "#ED6495",
            "line-style": "solid",
            "curve-style": "bezier",
            "target-arrow-shape": "circle",
            "target-arrow-color": "#ED6495",
        }
    },
    {
        "selector": "edge[interaction='constitutively upstream of']",
        "style": {
            "width": 3,
            "line-color": "#95E095",
            "line-style": "dashed",
            "curve-style": "bezier",
            "target-arrow-shape": "circle",
            "target-arrow-color": "#95E095",
        }
    },
    {
        "selector": 'edge[interaction="causally upstream of, negative effect"]',
        "style": {
            "width": 3,
            "line-color": "#95E095",
            "line-style": "dashed",
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#95E095",
        }
    },
    {
        "selector": 'edge[interaction="causally upstream of, positive effect"]',
        "style": {
            "width": 3,
            "line-color": "#FF9999",
            "line-style": "dashed",
            "curve-style": "bezier",
            "target-arrow-shape": "tee",
            "target-arrow-color": "#FF9999",
        }
    }
]

STYLE_SHEET = NODE_STYLES + EDGE_STYLES

# ================================= Layout Configuration =================================
LAYOUT_CONFIG = {
    "name": "klay",
    "fit": True,
    "padding": 5,
    "klay": {
        "direction": "DOWN",
        "spacing": 40,
        "edgeSpacingFactor": 0.5
    }
}

# ================================ Functions =================================
@st.cache_data
def parse_gocam_model(yaml_file_path: Path) -> Model:
    """Parse a GO-CAM model from a YAML file."""
    with open(yaml_file_path, 'r') as file:
        model_data = yaml.safe_load(file)
    model = Model.model_validate(model_data)
    return model

@st.cache_data
def load_all_gocam_models(directory_path: Path) -> dict:
    """Load all GO-CAM models from a specified directory."""
    models = {}
    for file_path in directory_path.glob('*.yaml'):
        model = parse_gocam_model(file_path)
        models[model.title] = {
            "model": model,
            "id": model.id,
            "title": model.title,
            "status": model.status.title() if model.status else "Unknown",
            "date": model.provenances[0].date if model.provenances else "Unknown"
        }
    return models

@st.cache_data
def convert_model_to_cytoscape_elements(model: Model):
    """Convert a GO-CAM model to Cytoscape elements."""
    cx2_network = model_to_cx2(model, 
                               validate_iquery_gene_symbol_pattern=True,
                               apply_dot_layout=False)
    elements = []
    for fragment in cx2_network:
        if 'nodes' in fragment:
            for node in fragment['nodes']:
                node_attrs = node.get('v', {})
                elements.append({
                    "data": {
                        "id": str(node['id']),
                        "label": node_attrs.get('name', str(node['id'])),
                        "represents": node_attrs.get('represents', ''),
                        "type": node_attrs.get('type', 'gene')
                    }
                })
        if 'edges' in fragment:
            for edge in fragment['edges']:
                edge_attrs = edge.get('v', {})
                elements.append({
                    "data": {
                        "id": f"e{edge['id']}",
                        "source": str(edge['s']),
                        "target": str(edge['t']),
                        "interaction": edge_attrs.get('name', '')
                    }
                })
    return elements

def display_gocam_network(
    elements: list,
    layout_config: dict = LAYOUT_CONFIG,
    stylesheet: list = STYLE_SHEET
):
    """Display the GO-CAM network using Streamlit Cytoscape component."""
    selected = cytoscape(
        elements,
        stylesheet,
        key="graph",
        layout=layout_config,
        height="900px",
        min_zoom=0.6,
        max_zoom=3
    )
    return selected
# %%
