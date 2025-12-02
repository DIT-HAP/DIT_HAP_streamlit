"""

"""

# ================================= Imports =================================
import streamlit as st
import yaml
from pathlib import Path

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from gocam.datamodel import Model
from gocam.translation.cx2.main import model_to_cx2
from st_cytoscape import cytoscape

# ================================ Constants =================================
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

GENE_LEVEL_DATA_FILE = Path(__file__).parent.parent / "data" / "raw" / "HD_DIT_HAP" / "gene_level" / "kmeans_cluster_result.tsv"

# ================================ Color Mapping =================================
def get_color_for_value(feature: str, value) -> str:
    """Get color for a specific value of a feature."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return '#CCCCCC'
    
    config = ADDTIONAL_METRICS_VISUALIZATION.get(feature)
    if not config:
        return '#CCCCCC'
    
    if config["type"] == "categorical":
        color_map = config.get("color_map", {})
        return color_map.get(str(value), color_map.get("default", "#CCCCCC"))
    
    # numerical type
    cmap, norm = config["colormap"]
    vmin, vmax = config["range"]
    clamped_val = max(vmin, min(vmax, float(value)))
    return mcolors.rgb2hex(cmap(norm(clamped_val))[:3])

def apply_color_mapping_to_styles(
    base_styles: list,
    elements: list,
    fill_feature: str | None = None,
    border_feature: str | None = None,
    label_feature: str | None = None
) -> list:
    """Apply color mapping to node styles based on selected features."""
    new_styles = base_styles.copy()
    
    for elem in elements:
        if 'data' not in elem or 'type' not in elem['data']:
            continue
            
        node_id = elem['data']['id']
        style = {}
        
        if fill_feature and fill_feature != "None":
            val = elem['data'].get(fill_feature)
            style["background-color"] = get_color_for_value(fill_feature, val)
        
        if border_feature and border_feature != "None":
            val = elem['data'].get(border_feature)
            style["border-color"] = get_color_for_value(border_feature, val)
            style["border-width"] = 2
        
        if label_feature and label_feature != "None":
            val = elem['data'].get(label_feature)
            style["color"] = get_color_for_value(label_feature, val)
        
        if style:
            new_styles.append({"selector": f"node[id='{node_id}']", "style": style})
    
    return new_styles

# ================================ Style Configuration =================================
NODE_STYLES = [
    {
        "selector": "node[type='gene']",
        "style": {
            "shape": "ellipse",
            "background-color": "#C8E6C9",
            "label": "data(label)",
            "color": "#000000",
            "text-valign": "center",
            "text-halign": "left",
            "width": 50,
            # "text-wrap": "wrap",
            # "text-max-width": "10px",
            # "text-justification": "center"
            # "width": calculate_node_width("data(label)")
        }
    },
    {
        "selector": "node[type='complex']",
        "style": {
            "shape": "rectangle",
            "background-color": "#E2BDE7",
            "label": "data(label)",
            "color": "#000000",
            "text-valign": "center",
            "text-halign": "left",
            "width": 70
        }
    },
    {
        "selector": "node[type='molecule']",
        "style": {
            "shape": "rectangle",
            "background-color": "#B2DFDB",
            "label": "data(label)",
            "color": "#000000",
            "text-valign": "center",
            "text-halign": "left",
            "width": 60,
            "text-wrap": "wrap",
            "text-max-width": "50px",
            "text-overflow-wrap": "anywhere",
            # "text-justification": "center"
        }
    }
]

EDGE_NAMES = {
    'directly positively regulates': {
        'description': 'direct positive regulation/activation',
        'color': '#008800',
        'style': 'solid',
        'arrowhead': 'normal',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'directly negatively regulates': {
        'description': 'direct negative regulation/inhibition',
        'color': '#FF0000',
        'style': 'solid',
        'arrowhead': 'tee',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'indirectly positively regulates': {
        'description': 'indirect positive regulation',
        'color': '#008800',
        'style': 'dashed',
        'arrowhead': 'normal',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'indirectly negatively regulates': {
        'description': 'indirect negative regulation',
        'color': '#FF0000',
        'style': 'dashed',
        'arrowhead': 'tee',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'provides input for': {
        'description': 'provides input for',
        'color': '#800080',
        'style': 'solid',
        'arrowhead': 'diamond',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'removes input for': {
        'description': 'removes input for',
        'color': '#FF9999',
        'style': 'solid',
        'arrowhead': 'box',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'has input': {
        'description': 'input of',
        'color': '#6495ED',
        'style': 'solid',
        'arrowhead': 'none',
        'arrowtail': 'dot',
        'dir': 'back'
    },
    'has output': {
        'description': 'has output',
        'color': '#ED6495',
        'style': 'solid',
        'arrowhead': 'dot',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'constitutively upstream of': {
        'description': 'constitutively upstream',
        'color': '#95E095',
        'style': 'dashed',
        'arrowhead': 'dot',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'causally upstream of, negative effect': {
        'description': 'upstream positive effect',
        'color': '#95E095',
        'style': 'dashed',
        'arrowhead': 'normal',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    'causally upstream of, positive effect': {
        'description': 'upstream negative effect',
        'color': '#FF9999',
        'style': 'dashed',
        'arrowhead': 'tee',
        'dir': 'forward',
        'arrowtail': 'none'
    },
    
}

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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
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
            "text-halign": "left",
            "color": "#000000"
        }
    }
]

STYLE_SHEET = NODE_STYLES + EDGE_STYLES

# ================================= Layout Configuration =================================
LAYOUT_CONFIG = {
    "name": "klay",
    "fit": True,
    "padding": 10,
    "nodeDimensionsIncludeLabels": True,
    # "spacingFactor": 1,
    "klay": {
        "direction": "DOWN",
        "edgeSpacingFactor": 1.5,
        "inLayerSpacingFactor": 1,
        "aspectRatio": 0.1,
        "borderSpacing": 30,
        "spacing": 30
    }
}

# All available layout configurations
AVAILABLE_LAYOUTS = {
    "klay": {
        "name": "klay",
        "description": "Layered graph drawing algorithm (hierarchical)",
        "config": {
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
    },
    "dagre": {
        "name": "dagre",
        "description": "Directed acyclic graph layout",
        "config": {
            "name": "dagre",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "rankDir": "TB",
            "ranker": "network-simplex",
            "nodeSep": 50,
            "rankSep": 50
        }
    },
    "cose": {
        "name": "cose",
        "description": "Compound Spring Embedder (force-directed)",
        "config": {
            "name": "cose",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "nodeRepulsion": 4500,
            "nodeOverlap": 10,
            "idealEdgeLength": 50,
            "edgeElasticity": 100,
            "nestingFactor": 5,
            "gravity": 80,
            "numIter": 1000,
            "animate": False
        }
    },
    "fcose": {
        "name": "fcose",
        "description": "Fast Compound Spring Embedder",
        "config": {
            "name": "fcose",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "animate": False,
            "animationDuration": 0,
            "quality": "default",
            "nodeRepulsion": 4500,
            "idealEdgeLength": 50,
            "edgeElasticity": 0.45,
            "nestingFactor": 0.1,
            "gravity": 0.25,
            "gravityRangeCompound": 1.5,
            "gravityCompound": 1.0
        }
    },
    "cola": {
        "name": "cola",
        "description": "Constraint-based layout using WebCola",
        "config": {
            "name": "cola",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "animate": False,
            "maxSimulationTime": 4000,
            "nodeSpacing": 20,
            "edgeLength": 100,
            "avoidOverlap": True,
            "convergenceThreshold": 0.01
        }
    },
    "breadthfirst": {
        "name": "breadthfirst",
        "description": "Hierarchical tree layout (BFS-based)",
        "config": {
            "name": "breadthfirst",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "directed": True,
            "spacingFactor": 1.0,
            "avoidOverlap": True,
            "maximal": False
        }
    },
    "circle": {
        "name": "circle",
        "description": "Nodes arranged in a circle",
        "config": {
            "name": "circle",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "avoidOverlap": True,
            "startAngle": 4.712,
            "clockwise": True
        }
    },
    "concentric": {
        "name": "concentric",
        "description": "Nodes in concentric circles by centrality",
        "config": {
            "name": "concentric",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "avoidOverlap": True,
            "minNodeSpacing": 10,
            "startAngle": 4.712,
            "clockwise": True,
            "equidistant": False
        }
    },
    "grid": {
        "name": "grid",
        "description": "Nodes arranged in a grid pattern",
        "config": {
            "name": "grid",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True,
            "avoidOverlap": True,
            "condense": False
        }
    },
    "random": {
        "name": "random",
        "description": "Randomly placed nodes",
        "config": {
            "name": "random",
            "fit": True,
            "padding": 10,
            "nodeDimensionsIncludeLabels": True
        }
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
            "title": model.title.strip(),
            "status": model.status.title() if model.status else "Unknown",
            "date": model.provenances[0].date if model.provenances else "Unknown"
        }
    return models

@st.cache_data
def deduplicate_cx2_edges(cx2_data: list) -> list:
    """Deduplicate edges in CX2 data by merging evidence for identical edges."""
    edge_aspect = next((aspect for aspect in cx2_data if "edges" in aspect), None)
    if not edge_aspect:
        return cx2_data
    
    # Group edges by source, target, and name
    edge_groups = {}
    for edge in edge_aspect["edges"]:
        key = (edge["s"], edge["t"], edge["v"].get("name"))
        if key not in edge_groups:
            edge_groups[key] = []
        edge_groups[key].append(edge)
    
    deduplicates_removed_edges = []
    for key, edges in edge_groups.items():
        if len(edges) == 1:
            deduplicates_removed_edges.extend(edges)
        else:
            base_edge = edges[0].copy()
            combined_evidence = []
            for edge in edges:
                evidence = edge["v"].get("Evidence", "")
                if evidence:
                    combined_evidence.append(evidence)
            
            if combined_evidence:
                # Parse and combine evidence HTML
                combined_li_items = []
                for evidence in combined_evidence:
                    soup = BeautifulSoup(evidence, 'html.parser')
                    # Extract all <li> items from this evidence
                    li_items = soup.find_all('li')
                    combined_li_items.extend(li_items)

                # Create a new combined HTML with all <li> items
                if combined_li_items:
                    combined_ul = BeautifulSoup('<ul style="padding-inline-start: 1rem"></ul>', 'html.parser').ul
                    for li in combined_li_items:
                        combined_ul.append(li)
                    base_edge["v"]["Evidence"] = str(combined_ul)
            
            deduplicates_removed_edges.append(base_edge)
    
    edge_aspect["edges"] = deduplicates_removed_edges
    return cx2_data

@st.cache_data
def add_additional_attributes(
    gene_level_data_file: Path,
) -> dict:
    """Add additional attributes to nodes based on external gene-level data."""
    if gene_level_data_file.name.endswith('.tsv'):
        additional_data = pd.read_csv(gene_level_data_file, index_col=1, sep='\t')
    elif gene_level_data_file.name.endswith('.csv'):
        additional_data = pd.read_csv(gene_level_data_file, index_col=1)
    elif gene_level_data_file.name.endswith('.xlsx'):
        additional_data = pd.read_excel(gene_level_data_file, index_col=1)
    else:
        raise ValueError("Unsupported file format for gene level data.")
    additional_data_dict = {}
    for metric in ADDITIONAL_METRICS:
        if metric in additional_data.columns:
            additional_data_dict[metric] = additional_data[metric].to_dict()
    return additional_data_dict

def calculate_additional_attributes(
    node: dict,
    additional_attributes: dict
) -> dict:
    """Calculate and add additional attributes to nodes in elements_dict."""
    node_type = node['type']
    
    if node_type == "gene":
        gene_id = node['label']
        for metric in ADDITIONAL_METRICS:
            metric_dict = additional_attributes.get(metric)
            if metric_dict:
                node[metric] = metric_dict.get(gene_id)
    
    elif node_type == "complex" and "member" in node:
        genes = node['member']
        for metric in ADDITIONAL_METRICS:
            metric_dict = additional_attributes.get(metric)
            if not metric_dict:
                continue
            
            gene_features = []
            member_metric = []
            for gene_name in genes:
                feature = metric_dict.get(gene_name)
                if feature is not None:
                    gene_features.append(feature)
                    member_metric.append(feature)
                else:
                    member_metric.append(None)
            
            if gene_features:
                if isinstance(gene_features[0], (int, float)):
                    node[metric] = round(sum(gene_features) / len(gene_features), 3)
                elif isinstance(gene_features[0], str):
                    node[metric] = ";".join(set(gene_features))
                else:
                    node[metric] = gene_features
            node["member_" + metric] = member_metric
    
    elif node_type == "molecule":
        molecule_name = node['label']
        for metric in ADDITIONAL_METRICS:
            metric_dict = additional_attributes.get(metric)
            if metric_dict:
                node[metric] = metric_dict.get(molecule_name)

    return node

@st.cache_data
def convert_model_to_cytoscape_elements(model: Model) -> tuple[list, dict]:
    """Convert a GO-CAM model to Cytoscape elements."""
    cx2_network = model_to_cx2(model, 
                               validate_iquery_gene_symbol_pattern=True,
                               apply_dot_layout=False)
    cx2_network = deduplicate_cx2_edges(cx2_network)

    additional_attributes = add_additional_attributes(GENE_LEVEL_DATA_FILE)

    elements = []
    elements_dict = {}
    
    # Pre-define keys to exclude for efficiency
    node_exclude_keys = {'name', 'type', 'represents', 'member'}
    edge_exclude_keys = {'name'}
    
    for fragment in cx2_network:
        if 'nodes' in fragment:
            for node in fragment['nodes']:
                node_id = str(node['id'])
                node_attrs = node.get('v', {})
                
                new_node_attrs = {
                    "id": node_id,
                    "label": node_attrs.get('name', node_id),
                    "type": node_attrs.get('type', 'gene'),
                    "represents": node_attrs.get('represents', '').removeprefix("PomBase:"),
                }
                
                if 'member' in node_attrs:
                    new_node_attrs['member'] = node_attrs['member']
                
                calculate_additional_attributes(new_node_attrs, additional_attributes)
                
                # Add remaining attributes
                for k, v in node_attrs.items():
                    if k not in node_exclude_keys:
                        new_node_attrs[k] = v
                
                elem = {"data": new_node_attrs}
                elements.append(elem)
                elements_dict[node_id] = elem
        
        elif 'edges' in fragment:
            for edge in fragment['edges']:
                edge_id = f"e{edge['id']}"
                edge_attrs = edge.get('v', {})
                
                new_edge_attrs = {
                    "id": edge_id,
                    "source": str(edge['s']),
                    "target": str(edge['t']),
                    "interaction": edge_attrs.get('name', '')
                }
                
                # Add remaining attributes
                for k, v in edge_attrs.items():
                    if k not in edge_exclude_keys:
                        new_edge_attrs[k] = v
                
                elem = {"data": new_edge_attrs}
                elements.append(elem)
                elements_dict[edge_id] = elem
    
    return elements, elements_dict

# @st.cache_data
def plot_interaction_type_legend():
    """Plot a legend for interaction types with alternating edge lines and labels."""
    legend_elements = []
    
    # First, add all the nodes (one pair per interaction type)
    node_pairs = []
    for i, edge_style in enumerate(EDGE_STYLES):
        selector = edge_style['selector']
        # Handle both single and double quotes in selector
        if 'edge[interaction="' in selector:
            interaction_type = selector.split('edge[interaction="')[1].split('"]')[0]
        elif "edge[interaction='" in selector:
            interaction_type = selector.split("edge[interaction='")[1].split("']")[0]
        else:
            continue  # Skip if selector doesn't match expected format
        
        # Create source and target nodes for the edge line
        source_id = f"legend_source_{i}"
        target_id = f"legend_target_{i}"
        # Create nodes for the label on the next row
        label_source_id = f"legend_label_source_{i}"
        label_target_id = f"legend_label_target_{i}"
        
        node_pairs.append((source_id, target_id, label_source_id, label_target_id, interaction_type))
        
        # Add nodes for edge line
        legend_elements.append({
            "data": {"id": source_id, "label": ""}
        })
        legend_elements.append({
            "data": {"id": target_id, "label": ""}
        })
        # Add nodes for label line
        legend_elements.append({
            "data": {"id": label_source_id, "label": ""}
        })
        legend_elements.append({
            "data": {"id": label_target_id, "label": EDGE_NAMES[interaction_type]['description']}
        })
    
    # Then add all the edges (interaction lines only)
    for i, (source_id, target_id, _, _, interaction_type) in enumerate(node_pairs):
        legend_elements.append({
            "data": {
                "id": f"legend_edge_{i}",
                "source": source_id,
                "target": target_id,
                "interaction": interaction_type,
            }
        })
    
    # Create legend-specific stylesheet
    legend_stylesheet = [
        {
            "selector": "node",
            "style": {
                "opacity": 0,
                "width": 1,
                "height": 1
            }
        },
        {
            "selector": "node[label]",
            "style": {
                "opacity": 1,
                "label": "data(label)",
                "text-halign": "left",
                "text-valign": "center",
                "color": "var(--text-color)",  # Adapts to Streamlit theme
                "font-size": "14px",
                "background-opacity": 0,
                "width": 1,
                "height": 1
            }
        },
        {
            "selector": "edge",
            "style": {
                "width": 4,
            }
        }
    ] + EDGE_STYLES
    
    # Calculate positions: alternating rows for edges and labels
    positions = {}
    row_spacing = 35
    for i, (source_id, target_id, label_source_id, label_target_id, _) in enumerate(node_pairs):
        row_index = i * 2  # Each interaction takes 2 rows
        # Edge line on even rows (left-aligned)
        positions[source_id] = {"x": 2, "y": row_index * row_spacing + 20}
        positions[target_id] = {"x": 150, "y": row_index * row_spacing + 20}
        # Label on odd rows (left-aligned)
        positions[label_source_id] = {"x": 2, "y": (row_index + 1) * row_spacing + 20}
        positions[label_target_id] = {"x": 160, "y": (row_index + 1) * row_spacing + 20}
    
    cytoscape(
        elements=legend_elements,
        stylesheet=legend_stylesheet,
        layout={
            "name": "preset",
            "positions": positions,
            "fit": True,
            "padding": 4
        },
        height=f"{len(node_pairs) * 2 * row_spacing + 40}px",
        key="legend",
        user_panning_enabled=False,
        user_zooming_enabled=False,
        selection_type="none",
    )


def plot_gradient_colorbar(feature: str, width: int = 200):
    """Plot a horizontal gradient colorbar for numerical features."""
    feature_config = ADDTIONAL_METRICS_VISUALIZATION.get(feature)
    if not feature_config or feature_config["type"] != "numerical":
        raise ValueError("Feature must be numerical and defined in ADDTIONAL_METRICS_VISUALIZATION.")
    else:
        vmin, vmax = feature_config["range"]
        cmap, norm = feature_config["colormap"]
        # Create horizontal gradient array
        gradient = np.linspace(vmin, vmax, width).reshape(1, -1)
        
        # Create figure
        with plt.rc_context(
            {
                'font.family': 'Arial',
                'font.size': 14,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'axes.spines.left': False,
                'axes.spines.bottom': False,
                'xtick.bottom': False,
                'ytick.left': False,
                'ytick.labelleft': False
            }
        ):
            fig, ax = plt.subplots(figsize=(7, 1), dpi=300)
            # Plot gradient
            ax.imshow(gradient, aspect='auto', cmap=cmap, norm=norm)
            # Configure axis
            n_ticks = 5
            tick_positions = np.linspace(0, width-1, n_ticks)
            tick_values = np.linspace(vmin, vmax, n_ticks)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels([f'{v:.2f}' for v in tick_values])
            plt.tight_layout()
        return fig

def plot_feature_color_legend(feature: str):
    """Plot color legend for a feature."""
    feature_type = ADDTIONAL_METRICS_VISUALIZATION.get(feature, {}).get("type")
    if feature_type == "numerical":
        # st.markdown(f"**Color Legend: {feature}**")
        fig = plot_gradient_colorbar(feature)
        st.pyplot(fig, width="content")
        plt.close(fig)
    elif feature_type == "categorical":
        st.markdown(f"**Color Legend: {feature}**")
        color_map = ADDTIONAL_METRICS_VISUALIZATION[feature].get("color_map", {})
        # Create a horizontal layout with flex wrap
        items_html = []
        for val, color in list(color_map.items())[:8]:  # Limit to 8 items
            items_html.append(
            f"<div style='display: flex; align-items: center; margin-right: 12px; margin-bottom: 4px;'>"
            f"<div style='width: 16px; height: 16px; background-color: {color}; border: 1px solid #666; margin-right: 6px;'></div>"
            f"<span style='font-size: 12px;'>{val}</span></div>"
            )
        
        st.markdown(f"<div style='display: flex; flex-wrap: wrap; align-items: center;'>{''.join(items_html)}</div>", 
               unsafe_allow_html=True)
        
        if len(color_map) > 8:
            st.markdown(f"<small style='font-size: 10px;'>... and {len(color_map) - 8} more</small>", unsafe_allow_html=True)
    

def node_color_mapping_panel(elements: list) -> tuple:
    """Create UI panel for node color mapping settings."""
    st.subheader("Node Color Mapping")
    
    feature_options = ["None"] + list(ADDTIONAL_METRICS_VISUALIZATION.keys())
    
    col1, col2 = st.columns([1, 2])
    col1.markdown(":blue-badge[**:material/highlight_mouse_cursor: Feature Selection**]")
    col2.markdown(":green-badge[**:material/gradient: Color Legend**]")
    
    col1_fill, col2_fill = st.columns([1, 2])
    fill_feature = col1_fill.selectbox("Fill color feature", feature_options, key="fill_feature")
    with col2_fill:
        plot_feature_color_legend(fill_feature)

    col1_border, col2_border = st.columns([1, 2])
    border_feature = col1_border.selectbox("Border color feature", feature_options, key="border_feature")
    with col2_border:
        plot_feature_color_legend(border_feature)
    
    col1_label, col2_label = st.columns([1, 2])
    label_feature = col1_label.selectbox("Label color feature", feature_options, key="label_feature")
    with col2_label:
        plot_feature_color_legend(label_feature)
    
    return fill_feature, border_feature, label_feature

def layout_selection_panel() -> dict:
    """Create UI panel for network layout selection."""
    st.subheader("Network Layout")
    
    # Layout selection
    layout_names = list(AVAILABLE_LAYOUTS.keys())
    layout_descriptions = {name: AVAILABLE_LAYOUTS[name]["description"] for name in layout_names}
    
    # Create display names with descriptions for selectbox
    selected_layout = st.selectbox(
        "Select layout algorithm",
        layout_names,
        index=0,  # Default to klay
        key="layout_selection",
        format_func=lambda x: f"{x} - {layout_descriptions[x]}"
    )
    
    # Get base config for selected layout
    layout_config = AVAILABLE_LAYOUTS[selected_layout]["config"].copy()
    
    # Layout-specific options
    with st.expander("Layout Options", expanded=False):
        if selected_layout == "klay":
            direction = st.selectbox(
                "Direction",
                ["DOWN", "UP", "LEFT", "RIGHT"],
                key="klay_direction"
            )
            spacing = st.slider("Spacing", 10, 100, 30, key="klay_spacing")
            layout_config["klay"] = layout_config.get("klay", {})
            layout_config["klay"]["direction"] = direction
            layout_config["klay"]["spacing"] = spacing
            layout_config["klay"]["borderSpacing"] = spacing
            
        elif selected_layout == "dagre":
            rank_dir = st.selectbox(
                "Rank Direction",
                ["TB", "BT", "LR", "RL"],
                format_func=lambda x: {"TB": "Top to Bottom", "BT": "Bottom to Top", 
                                       "LR": "Left to Right", "RL": "Right to Left"}[x],
                key="dagre_rankdir"
            )
            node_sep = st.slider("Node Separation", 10, 100, 50, key="dagre_nodesep")
            rank_sep = st.slider("Rank Separation", 10, 100, 50, key="dagre_ranksep")
            layout_config["rankDir"] = rank_dir
            layout_config["nodeSep"] = node_sep
            layout_config["rankSep"] = rank_sep
            
        elif selected_layout == "cose":
            node_repulsion = st.slider("Node Repulsion", 1000, 10000, 4500, step=500, key="cose_repulsion")
            ideal_edge_length = st.slider("Ideal Edge Length", 20, 150, 50, key="cose_edge_length")
            gravity = st.slider("Gravity", 10, 200, 80, key="cose_gravity")
            layout_config["nodeRepulsion"] = node_repulsion
            layout_config["idealEdgeLength"] = ideal_edge_length
            layout_config["gravity"] = gravity
            
        elif selected_layout == "fcose":
            quality = st.selectbox(
                "Quality",
                ["draft", "default", "proof"],
                index=1,
                key="fcose_quality"
            )
            node_repulsion = st.slider("Node Repulsion", 1000, 10000, 4500, step=500, key="fcose_repulsion")
            ideal_edge_length = st.slider("Ideal Edge Length", 20, 150, 50, key="fcose_edge_length")
            layout_config["quality"] = quality
            layout_config["nodeRepulsion"] = node_repulsion
            layout_config["idealEdgeLength"] = ideal_edge_length
            
        elif selected_layout == "cola":
            node_spacing = st.slider("Node Spacing", 5, 50, 20, key="cola_spacing")
            edge_length = st.slider("Edge Length", 50, 200, 100, key="cola_edge_length")
            layout_config["nodeSpacing"] = node_spacing
            layout_config["edgeLength"] = edge_length
            
        elif selected_layout == "breadthfirst":
            directed = st.checkbox("Directed", value=True, key="bf_directed")
            spacing_factor = st.slider("Spacing Factor", 0.5, 2.0, 1.0, step=0.1, key="bf_spacing")
            layout_config["directed"] = directed
            layout_config["spacingFactor"] = spacing_factor
            
        elif selected_layout == "circle":
            clockwise = st.checkbox("Clockwise", value=True, key="circle_clockwise")
            layout_config["clockwise"] = clockwise
            
        elif selected_layout == "concentric":
            min_spacing = st.slider("Minimum Node Spacing", 5, 50, 10, key="concentric_spacing")
            equidistant = st.checkbox("Equidistant", value=False, key="concentric_equidistant")
            layout_config["minNodeSpacing"] = min_spacing
            layout_config["equidistant"] = equidistant
            
        elif selected_layout == "grid":
            condense = st.checkbox("Condense", value=False, key="grid_condense")
            layout_config["condense"] = condense
        
        # Common options for all layouts
        st.divider()
        st.markdown("**Common Options**")
        padding = st.slider("Padding", 5, 50, 10, key="layout_padding")
        fit = st.checkbox("Fit to viewport", value=True, key="layout_fit")
        layout_config["padding"] = padding
        layout_config["fit"] = fit
    
    return layout_config


def display_gocam_network(
    elements: list,
    layout_config: dict = LAYOUT_CONFIG,
    stylesheet: list = STYLE_SHEET,
    key: str = "graph"
) -> dict:
    """Display the GO-CAM network using Streamlit Cytoscape component."""
    selected = cytoscape(
        elements,
        stylesheet,
        key=key,
        layout=layout_config,
        height="900px",
        min_zoom=0.5,
        max_zoom=3,
        user_panning_enabled=True,
        selection_type="single",
    )
    return selected

def display_selected_object(selected_elements: dict, elements_dict: dict):
    """Display details of the selected object in the network."""
    selected_nodes = selected_elements.get('nodes', [])
    selected_edges = selected_elements.get('edges', [])
    all_selected = selected_nodes + selected_edges
    if all_selected:
        for element_id in all_selected:
            element = elements_dict.get(element_id)
            if not element:
                continue
            data = element.get('data', {})
            for key, value in data.items():
                if key in ["id", "label", "type", "represents", "source", "target", "interaction", "member"] + ADDITIONAL_METRICS + MEMBER_METRICS:
                    if isinstance(value, list):
                        st.markdown(f"**{key}:** {', '.join(map(str, value))}")
                    else:
                        st.markdown(f"**{key}:** {value}")
                else:
                    st.markdown(f"**{key}:** ")
                    soup = BeautifulSoup(value, 'html.parser')
                    pretty_html = soup.prettify()
                    st.html(pretty_html)
    else:
        st.warning("No object selected.")

