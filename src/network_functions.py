# %% ================================= Imports =================================
import streamlit as st
import yaml
import json
from pathlib import Path
from typing import Any, Literal
from stqdm import stqdm
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from gocam.datamodel import Model
from gocam.translation.cx2.main import model_to_cx2
from st_cytoscape import cytoscape

# ================================= Constants =================================
GENE_LEVEL_DATA_FILE = Path(__file__).parent.parent / "data" / "raw" / "HD_DIT_HAP" / "gene_level" / "all_coding_genes_with_DIT_HAP_clustering.tsv"


ADDITIONAL_METRICS_CONFIG = {
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
        "range": ["E", "V", "V/E", "Not_determined"],
        "type": "categorical",
        "color_map": {
            "E": "#FF0000",  # Red for E/inviable
            "V": "#00FF00",  # Green for V/viable
            "V/E": "#FFA500",  # Orange for V/E/condition-dependent
            "Not_determined": "#CCCCCC"  # Gray for unknown
        }
    },
    "DR": {
        "range": (-0.3, 1.5),
        "type": "numerical",
        "colormap": [
            mcolors.LinearSegmentedColormap.from_list("bwr", ["#0000FF", "#FFFFFF", "#FF0000"]),
            mcolors.TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5)
        ]
    },
    "DL": {
        "range": (0, 13),
        "type": "numerical",
        "colormap": [
            mcolors.LinearSegmentedColormap.from_list("reds", ["#FF0000", "#00FF00"]),
            mcolors.Normalize(vmin=0, vmax=13)
        ]
    },
    "Cluster": {
        "range": None,
        "type": "categorical",
        "color_map": {
            "1": "#a50202",
            "2": "#d24c38",
            "3": "#d85b08",
            "4": "#ee8e19",
            "5": "#d6b200",
            "6": "#c6d70a",
            "7": "#5bd609",
            "8": "#00b9da",
            "9": "#0224bb",
        }
    }
}
ADDITIONAL_METRICS = list(ADDITIONAL_METRICS_CONFIG.keys())
MEMBER_METRICS = ["member_" + metric for metric in ADDITIONAL_METRICS]

# ============================ General Functions ============================
def _FILE_READERS(handler: str, file_path: str | Path, **kwargs) -> pd.DataFrame:
    """Reads different types of table files and returns a pandas DataFrame."""
    match handler:
        case "tsv":
            return pd.read_csv(file_path, sep="\t", index_col=0, **kwargs)
        case "csv":
            return pd.read_csv(file_path, index_col=0, **kwargs)
        case "xlsx":
            return pd.read_excel(file_path, index_col=0, **kwargs)
        case _:
            raise ValueError(f"Unsupported file handler: {handler}")

def get_theme_aware_label_color() -> tuple[str, str, str]:
    """Get appropriate label color and background color based on Streamlit theme."""
    _DEFAULT_COLOR = "#888888"
    streamlit_theme = st.context.theme.type
    try:
        if streamlit_theme == "dark":
            # return white text on black background
            return (_DEFAULT_COLOR, "#FFFFFF", "#000000")
        else:
            return (_DEFAULT_COLOR, "#000000", "#FFFFFF")
    except Exception:
        return (_DEFAULT_COLOR, "#000000", "#FFFFFF")

_DEFAULT_COLOR, THEME_COLOR, THEME_BACKGROUND = get_theme_aware_label_color()

# ================================= Interactive Panels =================================
def _plot_gradient_colorbar(feature: str, width: int = 200):
    """Plot a horizontal gradient colorbar for numerical features."""
    feature_config = ADDITIONAL_METRICS_CONFIG.get(feature)
    if not feature_config or feature_config["type"] != "numerical":
        return
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
    color_map = ADDITIONAL_METRICS_CONFIG[feature].get("color_map", {})
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
    feature_type = ADDITIONAL_METRICS_CONFIG.get(feature, {}).get("type")
    if feature_type == "numerical":
        _plot_gradient_colorbar(feature)
    elif feature_type == "categorical":
        _plot_categorical_color_legend(feature)
    else:
        pass

def node_color_mapping_panel() -> tuple:
    """Create UI panel for node color mapping settings."""
    st.subheader("Node Color Mapping")
    feature_options = ["None"] + list(ADDITIONAL_METRICS_CONFIG.keys())
    
    # st.markdown(":green-badge[**:material/gradient: Color Legend**]")
    
    fill_feature = st.selectbox(":blue-badge[**:material/contrast: Fill Color Feature**]", feature_options, key="fill_feature")
    plot_feature_color_legend(fill_feature)

    border_feature = st.selectbox(":green-badge[**:material/circle: Border Color Feature**]", feature_options, key="border_feature")
    plot_feature_color_legend(border_feature)
    
    label_feature = st.selectbox(":orange-badge[**:material/text_format: Label Color Feature**]", feature_options, key="label_feature")
    plot_feature_color_legend(label_feature)
    
    return fill_feature, border_feature, label_feature


    
# ============================ Parse Network ============================
@st.cache_data
def _parse_gocam_model(yaml_file_path: Path) -> Model:
    """Parse a GO-CAM model from a YAML file."""
    with open(yaml_file_path, 'r') as file:
        model_data = yaml.safe_load(file)
    model = Model.model_validate(model_data)
    return model

@st.cache_resource
def load_all_gocam_models(directory_path: Path) -> dict[str, dict]:
    """Load all GO-CAM models from a specified directory."""
    models = {}
    files = list(directory_path.glob('*.yaml'))
    for file in stqdm(files, desc="\nLoading GO-CAM models", st_container=st.container()):
        model = _parse_gocam_model(file)
        cx2_network = model_to_cx2(
            model,
            validate_iquery_gene_symbol_pattern=True,
            apply_dot_layout=True
        )
        models[model.title.strip()] = {
            "model": model,
            "id": model.id,
            "title": model.title.strip(),
            "status": model.status.title() if model.status else "Unknown",
            "date": model.provenances[0].date if model.provenances else "Unknown",
            "cx2_network": cx2_network
        }

    # sort by keys
    models = dict(sorted(models.items()))
    return models

@st.cache_data
def load_all_kegg_pathways(directory_path: Path) -> dict[str, list]:
    """Load all KEGG CX2 pathway files from a specified directory."""
    pathways = {}
    files = list(directory_path.glob('*.cx2'))
    for file in stqdm(files, desc="\nLoading KEGG pathways", st_container=st.container()):
        with open(file, 'r') as f:
            cx2_json = json.load(f)
            network_meta = cx2_json[3]["networkAttributes"][0]
            network_meta["name"] = network_meta["name"].removesuffix("_1")
            pathway_name = network_meta["name"]
            pathways[pathway_name] = network_meta
            pathways[pathway_name]["json"] = cx2_json
    # sort by keys
    pathways = dict(sorted(pathways.items()))
    return pathways


# ============================ Process Network ============================
# ---------------------------- Deduplicate CX2 Edges ----------------------------
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
        soup = BeautifulSoup(str(evidence), 'html.parser')
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

# ---------------------------- Merge Additional Attributes ----------------------------
@st.cache_data
def prepare_additional_attributes(gene_level_data_file: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load gene-level data and extract metrics as lookup dictionaries."""
    suffix = gene_level_data_file.suffix.lower()
    
    df = _FILE_READERS(
        handler=suffix.removeprefix('.'),
        file_path=gene_level_data_file
    )
    df["Cluster"] = df["Cluster"].fillna(0).astype(int)
    df.fillna("NA", inplace=True)
    df["Cluster"].replace(0, "NA", inplace=True)

    ID_dict = {
        metric: df[metric].to_dict()
        for metric in ADDITIONAL_METRICS
        if metric in df.columns
    }

    name_as_index_df = df.reset_index().set_index('Name')
    name_dict = {
        metric: name_as_index_df[metric].to_dict()
        for metric in ADDITIONAL_METRICS
        if metric in name_as_index_df.columns
    }

    return ID_dict, name_dict

def _aggregate_metric_values(values: list, data_type: str) -> Any:
    """Aggregate metric values based on their type."""
    if not values:
        return None
    
    if data_type == "numerical":
        valid_values = [v for v in values if isinstance(v, (int, float))]
        if not valid_values:
            return None
        return round(sum(valid_values) / len(valid_values), 3)
    elif data_type == "categorical":
        return ";".join(map(str, set(values)))
    return values

def _enrich_complex_node(node: dict, additional_attributes: dict) -> None:
    """Add metrics to a complex node by aggregating member values."""
    members = node['member']
    for metric, metric_dict in additional_attributes.items():
        # Collect values for each member (None if not found)
        member_values = [metric_dict.get(gene) for gene in members]
        valid_values = [v for v in member_values if v is not None and v != "NA"]
        
        # Store aggregated value and per-member breakdown
        node[metric] = _aggregate_metric_values(valid_values, ADDITIONAL_METRICS_CONFIG[metric]["type"])
        node[f"member_{metric}"] = member_values

def _enrich_gene_or_molecule_node(node: dict, additional_attributes: dict) -> None:
    """Add metrics to a gene node by direct lookup."""
    gene_id = node['represents']
    for metric, metric_dict in additional_attributes.items():
        node[metric] = metric_dict.get(gene_id)

# @st.cache_data
def calculate_additional_attributes_for_node(node: dict, additional_attributes: dict, name_attributes: dict) -> dict:
    """Enrich a node with additional metrics based on its type.   
    - gene: Direct lookup by gene represents
    - complex: Aggregate metrics from member genes
    - molecule: Direct lookup by molecule represents
    """
    node_type = node['type']
    
    # Handle complex nodes specially (need member check)
    if node_type == "complex" and "member" in node:
        _enrich_complex_node(node, name_attributes)
    else:
        # Use dispatch table for gene/molecule
        _enrich_gene_or_molecule_node(node, additional_attributes)
    
    return node

# ---------------------------- Convert CX2 to Cytoscape Elements ----------------------------
def _parse_cx2_node(node: dict, additional_attributes: dict, name_attributes: dict, pathway_type: Literal["go-cam", "kegg"]) -> dict:
    """Parse a single CX2 node into Cytoscape element format."""
    node_id = str(node['id'])
    attrs = node.get('v', {})
    
    if pathway_type == "go-cam":
        # Build core attributes
        data = {
            "id": node_id,
            "label": attrs.get('name', node_id),
            "type": attrs.get('type', 'gene'),
            "represents": attrs.get('represents', '').removeprefix("PomBase:"),
            "x": node.get('x', 0),
            "y": node.get('y', 0),
        }
        
        # Copy optional member list for complex nodes
        if 'member' in attrs:
            data['member'] = attrs['member']
        
        # Enrich with additional metrics (e.g., viability, cluster)
        calculate_additional_attributes_for_node(data, additional_attributes, name_attributes)
    
    elif pathway_type == "kegg":
        # Build core attributes
        label = attrs.get(
                'KEGG_NODE_LABEL_LIST_FIRST',
                attrs.get(
                    'KEGG_NODE_LABEL',
                    attrs.get(
                        'name',
                        attrs.get('KEGG_ID', node_id)
                    )))
        if isinstance(label, list):
            st.write(node)
            raise ValueError("Unexpected list type for KEGG_NODE_LABEL_LIST_FIRST")
        
        label = label.strip().removeprefix("SPOM_").removesuffix("...")
        KEGG_NODE_LABEL = attrs.get(
            "KEGG_NODE_LABEL_LIST",
            []
        )
        if len(KEGG_NODE_LABEL) >= 1:
            represents = KEGG_NODE_LABEL[-1].strip().removeprefix("SPOM_").removesuffix("...")
            if "." in represents:
                part1, part2 = represents.split(".")
                represents = part1.upper() + "." + part2.lower()
            else:
                represents = represents.upper()
        else:
            represents = label

        data = {
            "id": node_id,
            "label": label,
            "represents": represents,
            "type": attrs.get('KEGG_NODE_TYPE', 'unknown'),
            "x": node.get('x', 0),
            "y": node.get('y', 0),
        }
        
        # Enrich with additional metrics (e.g., viability, cluster)
        for metric, lookup in additional_attributes.items():
            if data["represents"] in lookup:
                value = lookup[data["represents"]]
                data[metric] = None if value == "NA" else value 
    else:
        raise ValueError(f"Unsupported pathway type: {pathway_type}")
    
    # Copy remaining attributes (excluding already-handled keys)
    for key, value in attrs.items():
        if key not in data:
            data[key] = value
    
    return {"data": data}


def _parse_cx2_edge(edge: dict, pathway_type: Literal["go-cam", "kegg"]) -> dict:
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

    if pathway_type == "go-cam":
        data['interaction'] = attrs.get('name', '')
    elif pathway_type == "kegg":
        data['interaction'] = attrs.get('interaction', '')
    else:
        raise ValueError(f"Unsupported pathway type: {pathway_type}")
    
    # Copy remaining attributes (excluding already-handled keys)
    for key, value in attrs.items():
        if key not in data:
            data[key] = value
    
    return {"data": data}


def _parse_cx2_network(cx2_network: list, additional_attributes: dict, name_attributes: dict, pathway_type: Literal["go-cam", "kegg"]) -> tuple[list, dict, dict]:
    """Parse CX2 network fragments into Cytoscape elements."""
    elements = []
    elements_dict = {}
    positions = {}
    
    for fragment in cx2_network:
        if 'nodes' in fragment:
            for node in fragment['nodes']:
                if node['v'].get('KEGG_NODE_LABEL_LIST_FIRST', '').startswith("TITLE:"):
                    continue  # Skip title nodes
                if node['v'].get('KEGG_NODE_TYPE', '') == 'ortholog':
                    continue  # Skip ortholog nodes
                elem = _parse_cx2_node(node, additional_attributes, name_attributes, pathway_type)
                positions[elem['data']['id']] = {
                    "x": int(elem['data'].get('x', 0)),
                    "y": int(elem['data'].get('y', 0)),
                }
                elements.append(elem)
                elements_dict[elem['data']['id']] = elem
        
        elif 'edges' in fragment:
            for edge in fragment['edges']:
                elem = _parse_cx2_edge(edge, pathway_type)
                elements.append(elem)
                elements_dict[elem['data']['id']] = elem
    
    return elements, elements_dict, positions

def convert_cx2_json_to_cytoscape_elements(cx2_network: list, pathway_type: Literal["go-cam", "kegg"]) -> tuple[list, dict, dict]:
    """Convert a cx2 json list to Cytoscape elements."""
    
    # Step 1: Merge duplicate edges
    cx2_network = deduplicate_cx2_edges(cx2_network)
    
    # Step 2: Load additional gene-level attributes
    additional_attributes, name_attributes = prepare_additional_attributes(GENE_LEVEL_DATA_FILE)
    
    # Step 3: Parse into Cytoscape elements
    elements, elements_dict, positions = _parse_cx2_network(cx2_network, additional_attributes, name_attributes, pathway_type)
    return elements, elements_dict, positions

# =============================== Node style mapping =================================
# -------------------------------- Node Style Configuration --------------------------------
def _get_color_for_value(feature: str, value: float | int | str | None, default_color: str = _DEFAULT_COLOR) -> str:
    """Map a feature value to a color.    
    - Categorical: lookup in color_map
    - Numerical: use colormap with normalization
    - Missing/None: return default gray
    """
    if value is None or (isinstance(value, float) and pd.isna(value)) or value == "NA":
        return default_color
    
    config = ADDITIONAL_METRICS_CONFIG.get(feature)
    if not config:
        return default_color
    
    if config["type"] == "categorical":
        color_map = config.get("color_map", {})
        return color_map.get(str(value), color_map.get("default", default_color))
    
    # Numerical
    cmap, norm = config["colormap"]
    vmin, vmax = config["range"]
    clamped = max(vmin, min(vmax, float(value)))
    return mcolors.rgb2hex(cmap(norm(clamped))[:3])

def map_feature_value(
    elements: list,
    fill_feature: str | None = None,
    border_feature: str | None = None,
    label_feature: str | None = None,
) -> tuple[list, list]:
    """Generate node styles, optionally with feature-based color mappings."""
    styles = []
    feature_mappings = [
        (fill_feature, "background-color", {}),
        (border_feature, "border-color", {"border-width": 2}),
        (label_feature, "color", {}),
    ]
    active_mappings = [(f, prop, extra) for f, prop, extra in feature_mappings 
                       if f and f != "None"]

    # Generate per-node style overrides
    for elem in elements:
        data = elem.get("data", {})
        if "type" not in data:
            continue  # Skip edges
        
        node_style = {}
        for feature, css_prop, extras in active_mappings:
            if feature == label_feature:
                node_style[css_prop] = _get_color_for_value(feature, data.get(feature), default_color=THEME_COLOR)
            elif feature == border_feature:
                node_style[css_prop] = _get_color_for_value(feature, data.get(feature))
            else:
                node_style[css_prop] = _get_color_for_value(feature, data.get(feature), default_color=THEME_BACKGROUND)
            node_style.update(extras)
        
        if node_style:
            styles.append({
                "selector": f"node[id='{data['id']}']",
                "style": node_style,
            })
    
    return active_mappings, styles

# %% =============================== Visualization Parameter Panel =================================
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
        # "acyclicer": "greedy",
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
        "edgeSpacingFactor": 2,
        "inLayerSpacingFactor": 1.5,
        "aspectRatio": 0.8,
        "borderSpacing": 30,
        "spacing": 30,
        "compactComponents": False,
    }
}

FCOSE_LAYOUT_CONFIG = {
    "name": "fcose",
    "fit": True,
    "padding": 10,
    "nodeDimensionsIncludeLabels": True,
    "fcose": {
        "quality": "default",
        "randomize": False,
        "fit": True,
        "padding": 10,
        "nodeSeparation": 80,
        "edgeElasticity": 0.45,
        "nestingFactor": 0.9,
        "gravity": 0.25,
        "numIter": 2500,
        "initialTemp": 200,
        "coolingFactor": 0.95,
        "minTemp": 1.75
    }
}



def layout_algorithm_panel() -> tuple[str, str | None]:
    """Create UI panel for layout algorithm selection. (preset for KEGG since it uses fixed positions)."""
    layout_type = st.selectbox(
        ":material/grid_view: **Layout Algorithm**",
        options=["Preset", "Dagre", "Klay", "fCose"],
        index=0,
        help="Select the graph layout algorithm:\n\n"
            "• **Preset**: Use original layout\n\n"
            "• **Dagre**: Directed acyclic graph layout with customizable ranking\n\n"
            "• **Klay**: Layer-based layout optimized for reducing edge crossings\n\n"
            "• **fCose**: Force-directed circular layout with physics simulation"
    )
    
    ranker = None
    if layout_type == "Dagre":
        ranker_options = {
            "Network Simplex": "network-simplex",
            "Longest Path": "longest-path",
            "Tight Tree": "tight-tree"
        }
        
        selected_display = st.selectbox(
            ":material/account_tree: **Ranker Algorithm** (Dagre only)",
            options=list(ranker_options.keys()),
            index=0,
            help="Select the algorithm for node ranking:\n\n"
                 "• **Network Simplex**: Balanced edge lengths (default)\n\n"
                 "• **Longest Path**: Nodes pushed to earliest possible layer (more compact vertically)\n\n"
                 "• **Tight Tree**: Compact tree structure"
        )
        ranker = ranker_options[selected_display]
    
    return layout_type.lower(), ranker

def get_layout_config(positions: dict, layout_type: str = "preset", ranker: str | None = None) -> dict:
    """Generate layout configuration with specified layout type and ranker method."""
    if layout_type == "preset":
        layout_config = {
            "name": "preset",
            "positions": positions,
            "fit": True,
            "padding": 10
        }
        return layout_config
    elif layout_type == "klay":
        return KLAY_LAYOUT_CONFIG.copy()
    elif layout_type == "fcose":
        return FCOSE_LAYOUT_CONFIG.copy()
    elif layout_type == "dagre":  # dagre
        config = LAYOUT_CONFIG.copy()
        config["config"] = config["config"].copy()
        if ranker:
            config["config"]["ranker"] = ranker
        return config
    else:
        raise ValueError(f"Unsupported layout type: {layout_type}")

# -------------------------------- Display Network --------------------------------
def display_network(
    elements: list,
    stylesheet: list,
    layout_config: dict,
    key: str = "graph",
) -> dict:
    """Display the network using st_cytoscape."""
    selected = cytoscape(
        elements,
        stylesheet,
        key=key,
        layout=layout_config,
        min_zoom=0.2,
        max_zoom=3,
        user_panning_enabled=True,
        height="1500px",
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
                    soup = BeautifulSoup(str(value), 'html.parser')
                    pretty_html = soup.prettify()
                    st.html(pretty_html)
    else:
        st.warning("No object selected.")


