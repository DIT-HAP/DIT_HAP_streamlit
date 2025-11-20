"""

"""

# ================================= Imports =================================
import streamlit as st
import yaml
from pathlib import Path
import colorsys

import pandas as pd
from bs4 import BeautifulSoup

from gocam.datamodel import Model
from gocam.translation.cx2.main import model_to_cx2
from st_cytoscape import cytoscape

# ================================ Constants =================================
ADDITIONAL_METRICS = [
    "FYPOviability",
    "RevisedDeletion_essentiality",
    "um",
    "lam",
    "revised_cluster"
]
MEMBER_METRICS = [ "member_" + metric for metric in ADDITIONAL_METRICS ]

GENE_LEVEL_DATA_FILE = Path(__file__).parent.parent / "data" / "raw" / "HD_DIT_HAP" / "gene_level" / "kmeans_cluster_result.tsv"

# ================================ Style Configuration =================================
def calculate_node_width(label_text: str, font_size: int = 10, padding: int = 10) -> float:
    """Calculate node width based on label text length."""
    char_width = font_size + len(label_text)**2 * 2
    min_width = 40
    calculated_width = max(char_width + padding, min_width)
    return calculated_width

NODE_STYLES = [
    {
        "selector": "node[type='gene']",
        "style": {
            "shape": "ellipse",
            "background-color": "#C8E6C9",
            "label": "data(label)",
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
            "text-valign": "center",
            "text-halign": "left",
            "width": 60
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
            "text-halign": "left"
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
    "spacingFactor": 1,
    "klay": {
        "direction": "DOWN",
        "edgeSpacingFactor": 1,
        "inLayerSpacingFactor": 1.2
        # "borderSpacing": 30,
        # "spacing": 30
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
                    soup = BeautifulSoup(evidence, 'lxml')
                    # Extract all <li> items from this evidence
                    li_items = soup.find_all('li')
                    combined_li_items.extend(li_items)

                # Create a new combined HTML with all <li> items
                if combined_li_items:
                    combined_ul = BeautifulSoup('<ul style="padding-inline-start: 1rem"></ul>', 'lxml').ul
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

@st.cache_data
def calculate_additional_attributes(
    node: dict,
    additional_attributes: dict
) -> dict:
    """Calculate and add additional attributes to nodes in elements_dict."""
    match node['type']:
        case "gene":
            gene_id = node['label']
            for metric in ADDITIONAL_METRICS:
                node[metric] = additional_attributes.get(metric, {}).get(gene_id)
        case "complex":
            if "member" in node:
                genes = node['member']
                for metric in ADDITIONAL_METRICS:
                    gene_features = []
                    member_metric = []
                    for gene_name in genes:
                        feature = additional_attributes.get(metric, {}).get(gene_name)
                        if feature is not None:
                            gene_features.append(feature)
                            member_metric.append(feature)
                        else:
                            member_metric.append(None)
                    if len(gene_features) > 0:
                        if isinstance(gene_features[0], (int, float)):
                            node[metric] = round(sum(gene_features) / len(gene_features), 3)
                        elif isinstance(gene_features[0], str):
                            node[metric] = ";".join(set(gene_features))
                        else:
                            node[metric] = gene_features
                    node["member_" + metric] = member_metric
        case "molecule":
            molecule_name = node['label']
            for metric in ADDITIONAL_METRICS:
                node[metric] = additional_attributes.get(metric, {}).get(molecule_name)
        
        case _:
            pass

    return node

@st.cache_data
def convert_model_to_cytoscape_elements(model: Model) -> tuple[list, dict]:
    """Convert a GO-CAM model to Cytoscape elements."""
    cx2_network = model_to_cx2(model, 
                               validate_iquery_gene_symbol_pattern=True,
                               apply_dot_layout=False)
    cx2_network = deduplicate_cx2_edges(cx2_network)

    additional_attributes = add_additional_attributes(GENE_LEVEL_DATA_FILE)

    elements_dict = {}
    elements = []
    for fragment in cx2_network:
        if 'nodes' in fragment:
            for node in fragment['nodes']:
                node_attrs = node.get('v', {})
                new_node_attrs = {}
                new_node_attrs = {
                    "id": str(node['id']),
                    "label": node_attrs.get('name', str(node['id'])),
                    "type": node_attrs.get('type', 'gene'),
                    "represents": node_attrs.get('represents', '').removeprefix("PomBase:"),
                }
                if 'member' in node_attrs:
                    new_node_attrs['member'] = node_attrs['member']
                new_node_attrs = calculate_additional_attributes(new_node_attrs, additional_attributes)
                new_node_attrs.update(
                    {k: v for k, v in node_attrs.items() if k not in ['name', 'type', 'represents', 'member']}
                )
                elements.append({
                    "data": new_node_attrs
                })
                elements_dict[str(node['id'])] = elements[-1]
        if 'edges' in fragment:
            for edge in fragment['edges']:
                edge_attrs = edge.get('v', {})
                new_edge_attrs = {
                    "id": f"e{edge['id']}",
                    "source": str(edge['s']),
                    "target": str(edge['t']),
                    "interaction": edge_attrs.get('name', '')
                }
                new_edge_attrs.update(
                    {k: v for k, v in edge_attrs.items() if k not in ['name']}
                )
                elements.append({
                    "data": new_edge_attrs
                })
                elements_dict[f"e{edge['id']}"] = elements[-1]
    return elements, elements_dict

# @st.cache_data
def plot_interaction_type_legend():
    """Plot a legend for interaction types."""
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
        
        # Create source and target nodes for this interaction type
        source_id = f"legend_source_{i}"
        target_id = f"legend_target_{i}"
        node_pairs.append((source_id, target_id, interaction_type))
        
        legend_elements.append({
            "data": {"id": source_id, "label": ""}
        })
        legend_elements.append({
            "data": {"id": target_id, "label": ""}
        })
    
    # Then add all the edges
    for i, (source_id, target_id, interaction_type) in enumerate(node_pairs):
        legend_elements.append({
            "data": {
                "id": f"legend_edge_{i}",
                "source": source_id,
                "target": target_id,
                "interaction": interaction_type,
                "label": EDGE_NAMES[interaction_type]['description']
            }
        })
    
    # Create legend-specific stylesheet with hidden nodes and edge labels
    legend_stylesheet = [
        {
            "selector": "node",
            "style": {
                "opacity": 0
            }
        },
        {
            "selector": "edge",
            "style": {
                "label": "data(label)",
                "text-rotation": "none",
                "text-margin-x": "160vw",
                "text-halign": "left",
                "text-valign": "left",
                "font-size": "14px"
            }
        }
    ] + EDGE_STYLES
    
    cytoscape(
        elements=legend_elements,
        stylesheet=legend_stylesheet,
        layout={
            "name": "preset",
            "positions": {node_pairs[i][0]: {"x": 20, "y": i * 40 + 20} for i in range(len(node_pairs))} |
                        {node_pairs[i][1]: {"x": 120, "y": i * 40 + 20} for i in range(len(node_pairs))},
            "fit": False
        },
        height=f"{len(node_pairs) * 40 + 40}px",
        key="legend",
        user_panning_enabled=False,
        user_zooming_enabled=False,
        selection_type="none",
    )


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
                    soup = BeautifulSoup(value, 'lxml')
                    pretty_html = soup.prettify()
                    st.html(pretty_html)
    else:
        st.warning("No object selected.")

