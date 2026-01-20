# %% ================================= Imports =================================
from .network_functions import (
    THEME_COLOR,
    THEME_BACKGROUND,
    map_feature_value
)

# %% =============================== Style sheet Configuration =================================
# ------------------------------- Default node styles -------------------------------
NODE_STYLES = [  
    {  
        "selector": "node:selected",  
        "style": {  
            "background-color": "#FFFF00"  
        }  
    },  
    {  
        "selector": "node[KEGG_NODE_TYPE = 'ortholog']",  
        "style": {  
            "label-font-size": 9,  
        }  
    },  
    {  
        "selector": "node[KEGG_NODE_TYPE = 'gene']",  
        "style": {  
            "label-font-size": 9  
        }  
    },  
    {  
        "selector": "node[KEGG_NODE_TYPE = 'map']",  
        "style": {  
            "label-font-size": 9  
        }  
    },  
    {  
        "selector": "node[KEGG_NODE_TYPE = 'compound']",  
        "style": {  
            "label-font-size": 6,  
            "border-width": 2.0,  
            "text-valign": "top",  
            "text-margin-y": 2.0  
        }  
    },  
    {  
        "selector": "node[KEGG_NODE_TYPE = 'group']",  
        "style": {  
            "label-font-size": 9,  
            "border-width": 1.0,  
            "background-opacity": 0.0  
        }  
    }  
]

# ------------------------------- Default edge styles -------------------------------
EDGE_STYLES = [
    {
        "selector": "edge",
        "style": {
            "width": 2,
            "line-color": THEME_COLOR,
            "line-style": "solid",
            "opacity": 0.7058823529411765,
            "curve-style": "bezier",
            "target-arrow-shape": "none",
            "target-arrow-color": THEME_COLOR,
            "target-arrow-size": 6.0,
            "source-arrow-shape": "none",
            "source-arrow-color": THEME_COLOR,
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
# ------------------------------- Generate node styles -------------------------------
def get_node_styles(
    elements: list,
    fill_feature: str | None = None,
    border_feature: str | None = None,
    label_feature: str | None = None,
) -> list:
    """Generate node styles, optionally with feature-based color mappings."""
    label_color = THEME_COLOR
    styles = []

    # Obtain preset positions
    for element in elements:
        element_data = element.get("data", {})
        node_id = element_data.get("id")
        fill_color = element_data.get("KEGG_NODE_FILL_COLOR", THEME_BACKGROUND)
        if fill_color == THEME_COLOR:
            fill_color = THEME_BACKGROUND  # Avoid same color as text
        label_color = element_data.get("KEGG_NODE_LABEL_COLOR", THEME_COLOR)
        if fill_color == THEME_BACKGROUND or fill_color == THEME_COLOR:
            label_color = THEME_COLOR

        width = int(element_data.get("KEGG_NODE_WIDTH", 10))
        height = int(element_data.get("KEGG_NODE_HEIGHT", 10))

        style = {
            "label": "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "shape": element_data.get("KEGG_NODE_SHAPE", "ellipse").lower(),
            "background-color": fill_color,
            "color": label_color,
            "border-color": THEME_COLOR,
            "border-width": 1,
            "width": width,
            "height": height,
        }
        styles.append({"selector": f"node[id='{node_id}']", "style": style})

    active_mapping, mapping_styles = map_feature_value(
        elements,
        fill_feature,
        border_feature,
        label_feature
    )
    if active_mapping:
        styles.extend(mapping_styles)
        return styles
    else:
        return styles

# ------------------------------- Generate complete stylesheet -------------------------------
def get_stylesheet(
    elements: list,
    fill_feature: str | None = None,
    border_feature: str | None = None,
    label_feature: str | None = None,
) -> list:
    """Generate complete Cytoscape stylesheet (nodes + edges) and positions."""
    node_styles = get_node_styles(elements, fill_feature, border_feature, label_feature)
    return NODE_STYLES + node_styles + EDGE_STYLES




# =============================== Plot Feature Color Legend =================================




