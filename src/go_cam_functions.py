# ================================= Imports =================================
import streamlit as st
import yaml
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from gocam.datamodel import Model
from gocam.translation.cx2.main import model_to_cx2
from st_cytoscape import cytoscape

# ================================ Simple Functions =================================
# File extension to pandas reader mapping
_FILE_READERS = {
    '.tsv': lambda f: pd.read_csv(f, index_col=1, sep='\t'),
    '.csv': lambda f: pd.read_csv(f, index_col=1),
    '.xlsx': lambda f: pd.read_excel(f, index_col=1),
}

# ================================ Constants =================================
# -------------------------------- Data File Paths --------------------------------
GENE_LEVEL_DATA_FILE = Path(__file__).parent.parent / "data" / "raw" / "HD_DIT_HAP" / "gene_level" / "kmeans_cluster_result.tsv"

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
        "fit": True,
        "padding": 10,
        "nodeDimensionsIncludeLabels": True,
        "rankDir": "TB",
        "ranker": "longest-path",
        "nodeSep": 50,
        "rankSep": 50
    }
}

# LAYOUT_CONFIG = {
#     "name": "klay",
#     "fit": True,
#     "padding": 10,
#     "nodeDimensionsIncludeLabels": True,
#     # "spacingFactor": 1,
#     "klay": {
#         "direction": "DOWN",
#         "edgeSpacingFactor": 1.5,
#         "inLayerSpacingFactor": 1,
#         "aspectRatio": 0.1,
#         "borderSpacing": 30,
#         "spacing": 30
#     }
# }

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

# -------------------------------- Node Type Configuration --------------------------------


# Node type configurations: maps type -> visual properties
_NODE_TYPE_CONFIG = {
    "gene":     {"shape": "ellipse",   "color": "#C8E6C9", "width": 50},
    "complex":  {"shape": "rectangle", "color": "#E2BDE7", "width": 70},
    "molecule": {"shape": "rectangle", "color": "#B2DFDB", "width": 60},
}

# Extra styles for specific node types
_NODE_TYPE_EXTRAS = {
    "molecule": {
        "text-wrap": "wrap",
        "text-max-width": "50px",
        "text-overflow-wrap": "-",
        "text-justification": "center",
    },
}

# -------------------------------- Edge Style Configuration --------------------------------
EDGE_NAMES = {
    'directly positively regulates': 'direct positive regulation/activation',
    'directly negatively regulates': 'direct negative regulation/inhibition',
    'indirectly positively regulates': 'indirect positive regulation',
    'indirectly negatively regulates': 'indirect negative regulation',
    'provides input for': 'provides input for',
    'removes input for': 'removes input for',
    'has input': 'input of',
    'has output': 'has output',
    'constitutively upstream of': 'constitutively upstream',
    'causally upstream of, negative effect': 'upstream positive effect',
    'causally upstream of, positive effect': 'upstream negative effect',
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
            "text-halign": "left",
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
        }
    }
]

# ================================ GO-CAM Related Functions =================================
@st.cache_data
def _parse_gocam_model(yaml_file_path: Path) -> Model:
    """Parse a GO-CAM model from a YAML file."""
    with open(yaml_file_path, 'r') as file:
        model_data = yaml.safe_load(file)
    model = Model.model_validate(model_data)
    return model

@st.cache_data
def load_all_gocam_models(directory_path: Path) -> dict[str, dict]:
    """Load all GO-CAM models from a specified directory."""
    models = {}
    for file_path in directory_path.glob('*.yaml'):
        model = _parse_gocam_model(file_path)
        models[model.title] = {
            "model": model,
            "id": model.id,
            "title": model.title.strip(),
            "status": model.status.title() if model.status else "Unknown",
            "date": model.provenances[0].date if model.provenances else "Unknown"
        }
    return models

# =============================== CX2 Related Functions =================================
def _group_edges_by_key(edges: list) -> dict[tuple, list]:
    """Group edges by (source, target, name) tuple."""
    groups = {}
    for edge in edges:
        key = (edge["s"], edge["t"], edge["v"].get("name"))
        groups.setdefault(key, []).append(edge)
    return groups

def _merge_evidence_html(evidence_list: list[str]) -> str:
    """Merge multiple HTML evidence strings into a single <ul> list."""
    all_li_items = []
    for evidence in evidence_list:
        soup = BeautifulSoup(evidence, 'html.parser')
        all_li_items.extend(soup.find_all('li'))
    
    if not all_li_items:
        return ""
    
    soup = BeautifulSoup('<ul style="padding-inline-start: 1rem"></ul>', 'html.parser')
    combined_ul = soup.find('ul')
    if combined_ul is None:
        return ""
    for li in all_li_items:
        combined_ul.append(li)
    return str(combined_ul)

def _merge_duplicate_edges(edge_groups: dict) -> list[dict]:
    """Merge duplicate edges, combining their evidence."""
    result = []
    for edges in edge_groups.values():
        if len(edges) == 1:
            result.extend(edges)
        else:
            # Merge duplicates: keep first edge, combine evidence
            merged = edges[0].copy()
            evidence_list = [e["v"].get("Evidence", "") for e in edges]
            if evidence_list:
                merged["v"]["Evidence"] = _merge_evidence_html(evidence_list)
            result.append(merged)
    return result

@st.cache_data
def deduplicate_cx2_edges(cx2_data: list) -> list[dict]:
    """
    Deduplicate edges in CX2 data by merging evidence for identical edges.
    Edges with the same (source, target, name) are merged into one, 
    with their Evidence HTML lists combined.
    """
    edge_aspect = next((aspect for aspect in cx2_data if "edges" in aspect), None)
    if not edge_aspect:
        return cx2_data

    edge_groups = _group_edges_by_key(edge_aspect["edges"])
    edge_aspect["edges"] = _merge_duplicate_edges(edge_groups)
    return cx2_data

# =============================== Additional Attributes =================================
@st.cache_data
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


def _aggregate_metric_values(values: list) -> Any:
    """Aggregate metric values based on their type."""
    if not values:
        return None
    
    first = values[0]
    if isinstance(first, (int, float)):
        return round(sum(values) / len(values), 3)
    elif isinstance(first, str):
        return ";".join(set(values))
    return values

def _enrich_complex_node(node: dict, additional_attributes: dict) -> None:
    """Add metrics to a complex node by aggregating member values."""
    members = node['member']
    for metric, metric_dict in additional_attributes.items():
        # Collect values for each member (None if not found)
        member_values = [metric_dict.get(gene) for gene in members]
        valid_values = [v for v in member_values if v is not None]
        
        # Store aggregated value and per-member breakdown
        node[metric] = _aggregate_metric_values(valid_values)
        node[f"member_{metric}"] = member_values

def _enrich_gene_or_molecule_node(node: dict, additional_attributes: dict) -> None:
    """Add metrics to a gene node by direct lookup."""
    gene_id = node['label']
    for metric, metric_dict in additional_attributes.items():
        node[metric] = metric_dict.get(gene_id)

# @st.cache_data
def calculate_additional_attributes_for_node(node: dict, additional_attributes: dict) -> dict:
    """Enrich a node with additional metrics based on its type.   
    - gene: Direct lookup by gene label
    - complex: Aggregate metrics from member genes
    - molecule: Direct lookup by molecule label
    """
    node_type = node['type']
    
    # Handle complex nodes specially (need member check)
    if node_type == "complex" and "member" in node:
        _enrich_complex_node(node, additional_attributes)
    else:
        # Use dispatch table for gene/molecule
        _enrich_gene_or_molecule_node(node, additional_attributes)
    
    return node

# ================================ CX2 to Cytoscape Conversion =================================
def _parse_cx2_node(node: dict, additional_attributes: dict) -> dict:
    """Parse a single CX2 node into Cytoscape element format."""
    node_id = str(node['id'])
    attrs = node.get('v', {})
    
    # Build core attributes
    data = {
        "id": node_id,
        "label": attrs.get('name', node_id),
        "type": attrs.get('type', 'gene'),
        "represents": attrs.get('represents', '').removeprefix("PomBase:"),
    }
    
    # Copy optional member list for complex nodes
    if 'member' in attrs:
        data['member'] = attrs['member']
    
    # Enrich with additional metrics (e.g., viability, cluster)
    calculate_additional_attributes_for_node(data, additional_attributes)
    
    # Copy remaining attributes (excluding already-handled keys)
    for key, value in attrs.items():
        if key not in data:
            data[key] = value
    
    return {"data": data}


def _parse_cx2_edge(edge: dict) -> dict:
    """Parse a single CX2 edge into Cytoscape element format."""
    edge_id = f"e{edge['id']}"
    attrs = edge.get('v', {})
    
    # Build core attributes
    data = {
        "id": edge_id,
        "source": str(edge['s']),
        "target": str(edge['t']),
        "interaction": attrs.get('name', ''),
    }
    
    # Copy remaining attributes (excluding already-handled keys)
    for key, value in attrs.items():
        if key not in data:
            data[key] = value
    
    return {"data": data}


def _parse_cx2_network(cx2_network: list, additional_attributes: dict) -> tuple[list, dict]:
    """Parse CX2 network fragments into Cytoscape elements."""
    elements = []
    elements_dict = {}
    
    for fragment in cx2_network:
        if 'nodes' in fragment:
            for node in fragment['nodes']:
                elem = _parse_cx2_node(node, additional_attributes)
                elements.append(elem)
                elements_dict[elem['data']['id']] = elem
        
        elif 'edges' in fragment:
            for edge in fragment['edges']:
                elem = _parse_cx2_edge(edge)
                elements.append(elem)
                elements_dict[elem['data']['id']] = elem
    
    return elements, elements_dict

# @st.cache_resource
def convert_model_to_cytoscape_elements(model: Model) -> tuple[list, dict]:
    """Convert a GO-CAM model to Cytoscape elements."""
    # Step 1: Convert model to CX2 format
    cx2_network = model_to_cx2(
        model,
        validate_iquery_gene_symbol_pattern=True,
        apply_dot_layout=False
    )
    
    # Step 2: Merge duplicate edges
    cx2_network = deduplicate_cx2_edges(cx2_network)
    
    # Step 3: Load additional gene-level attributes
    additional_attributes = prepare_additional_attributes(GENE_LEVEL_DATA_FILE)
    
    # Step 4: Parse into Cytoscape elements
    elements = _parse_cx2_network(cx2_network, additional_attributes)
    return elements

# =============================== Visualization Parameter Panel =================================
def node_color_mapping_panel() -> tuple:
    """Create UI panel for node color mapping settings."""
    st.subheader("Node Color Mapping")
    feature_options = ["None"] + list(ADDTIONAL_METRICS_VISUALIZATION.keys())
    
    # st.markdown(":green-badge[**:material/gradient: Color Legend**]")
    
    fill_feature = st.selectbox(":blue-badge[**:material/contrast: Fill Color Feature**]", feature_options, key="fill_feature")
    plot_feature_color_legend(fill_feature)

    border_feature = st.selectbox(":green-badge[**:material/circle: Border Color Feature**]", feature_options, key="border_feature")
    plot_feature_color_legend(border_feature)
    
    label_feature = st.selectbox(":orange-badge[**:material/text_format: Label Color Feature**]", feature_options, key="label_feature")
    plot_feature_color_legend(label_feature)
    
    return fill_feature, border_feature, label_feature

# ================================ Visualization Styles =================================

# -------------------------------- Node Style Configuration --------------------------------


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
    
    # 1. Generate base styles for each node type
    for node_type, config in _NODE_TYPE_CONFIG.items():
        style = {
            "label": "data(label)",
            "text-valign": "center",
            "text-halign": "left",
            "shape": config["shape"],
            "background-color": config["color"],
            "width": config["width"],
            "color": label_color,
            **_NODE_TYPE_EXTRAS.get(node_type, {}),
        }
        styles.append({"selector": f"node[type='{node_type}']", "style": style})
    
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
        return styles
    
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
    
    return styles

# -------------------------------- Complete Stylesheet Configuration --------------------------------
def get_stylesheet(
    elements: list | None = None,
    fill_feature: str | None = None,
    border_feature: str | None = None,
    label_feature: str | None = None,
) -> list:
    """Generate complete Cytoscape stylesheet (nodes + edges)."""
    node_styles = get_node_styles(elements, fill_feature, border_feature, label_feature)
    return node_styles + EDGE_STYLES

# =============================== Plot Feature Color Legend =================================
def _plot_gradient_colorbar(feature: str, width: int = 200):
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
            fig, ax = plt.subplots(figsize=(5, 1), dpi=300)
            # Plot gradient
            ax.imshow(gradient, aspect='auto', cmap=cmap, norm=norm)
            # Configure axis
            n_ticks = 5
            tick_positions = np.linspace(0, width-1, n_ticks)
            tick_values = np.linspace(vmin, vmax, n_ticks)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels([f'{v:.2f}' for v in tick_values])
            plt.tight_layout()

        st.pyplot(fig, width="stretch")
        plt.close(fig)

def _plot_categorical_color_legend(feature: str):
    """Plot color legend for categorical features."""
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

def plot_feature_color_legend(feature: str):
    """Plot color legend for a feature."""
    feature_type = ADDTIONAL_METRICS_VISUALIZATION.get(feature, {}).get("type")
    if feature_type == "numerical":
        _plot_gradient_colorbar(feature)
    elif feature_type == "categorical":
        _plot_categorical_color_legend(feature)
    else:
        pass

# ================================ Plot Interaction Type Legend =================================
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
            "data": {"id": label_target_id, "label": EDGE_NAMES[interaction_type]}
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
                "color": THEME_COLOR,  # Adapts to Streamlit theme
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

# ================================ Display GO-CAM Network =================================
def display_gocam_network(
    elements: list,
    stylesheet: list,
    layout_config: dict = LAYOUT_CONFIG,
    key: str = "graph"
) -> dict:
    """Display the GO-CAM network using Streamlit Cytoscape component."""
    selected = cytoscape(
        elements,
        stylesheet,
        key=key,
        layout=layout_config,
        min_zoom=0.5,
        max_zoom=3,
        user_panning_enabled=True,
        height="600px",
        selection_type="single",
    )
    return selected

# =============================== Display Selected Object Details =================================
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

