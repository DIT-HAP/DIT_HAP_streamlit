# ================================= Imports =================================
# from st_cytoscape import cytoscape
from .network_functions import (
    THEME_COLOR,
    THEME_BACKGROUND,
    map_feature_value
)

# ================================ Style sheet Configuration =================================
# ------------------------------- Default node styles -------------------------------
NODE_STYLES = [  
  # Default node styles  
  {  
    "selector": "node",  
    "style": {  
      "background-color": "#FFFFFF",  
      "background-opacity": 1,  
      "border-color": "#CCCCCC",  
      "border-opacity": 1,  
      "border-style": "solid",  
      "border-width": 1,  
      "height": 35,  
      "width": 75,  
      "shape": "round-rectangle",  
      "label": "data(name)",  
      "color": "#000000",  
      "font-size": 12,  
      "font-family": "sans-serif",  
      "text-opacity": 1,  
      "text-max-width": 200,  
      "text-valign": "center",  
      "text-halign": "center"  
    }  
  },  

  # Node type mappings  
  {  
    "selector": "node[type='gene']",  
    "style": {  
      "background-color": "#C8E6C9",  
      "height": 40,  
      "width": 85,  
      "shape": "rectangle",  
      "font-size": 12,  
      "text-max-width": 80  
    }  
  },  
  {  
    "selector": "node[type='complex']",  
    "style": {  
      "background-color": "#E2BDE7",  
      "height": 70,  
      "width": 110,  
      "shape": "rectangle",  
      "font-size": 15,  
      "text-max-width": 100,
      "text-wrap": "wrap",
      "text-overflow-wrap": "whitespace",
      "text-justification": "center"
    }  
  },  
  {  
    "selector": "node[type='molecule']",  
    "style": {  
      "background-color": "#B2DFDB",  
      "height": 40,  
      "width": 70,  
      "shape": "ellipse",  
      "font-size": 10,  
      "text-max-width": 70,
      "text-wrap": "wrap",
      "text-overflow-wrap": "anywhere",
      "text-justification": "center"
    }  
  },
]

# ------------------------------- Default edge styles -------------------------------
EDGE_STYLES = [
  # Default edge styles  
  {  
    "selector": "edge",  
    "style": {  
      "curve-style": "bezier",  
      "line-color": "#848484",  
      "line-style": "solid",  
      "width": 2,  
      "opacity": 1,  
      "target-arrow-shape": "none",  
      "target-arrow-color": "#000000",  
      "source-arrow-shape": "none",  
      "source-arrow-color": "#000000"  
    }  
  },  

  # Edge represents mappings - RO:0002304  
  {  
    "selector": "edge[represents='RO:0002304']",  
    "style": {  
      "line-color": "#95e095",  
      "line-style": "dashed",  
      "target-arrow-shape": "triangle",  
      "target-arrow-color": "#95e095",  
      "width": 5  
    }  
  },

  # Edge represents mappings - RO:0002305  
  {  
    "selector": "edge[represents='RO:0002305']",  
    "style": {  
      "line-color": "#fF9999",  
      "line-style": "dashed",  
      "target-arrow-shape": "tee",  
      "target-arrow-color": "#fF9999",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0012009  
  {  
    "selector": "edge[represents='RO:0012009']",  
    "style": {  
      "line-color": "#95e095",  
      "line-style": "dashed",  
      "target-arrow-shape": "circle",  
      "target-arrow-color": "#95e095",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002630  
  {  
    "selector": "edge[represents='RO:0002630']",  
    "style": {  
      "line-color": "#FF0000",  
      "line-style": "solid",  
      "target-arrow-shape": "tee",  
      "target-arrow-color": "#FF0000",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002629  
  {  
    "selector": "edge[represents='RO:0002629']",  
    "style": {  
      "line-color": "#008800",  
      "line-style": "solid",  
      "target-arrow-shape": "triangle",  
      "target-arrow-color": "#008800",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002233  
  {  
    "selector": "edge[represents='RO:0002233']",  
    "style": {  
      "line-color": "#6495ED",  
      "line-style": "solid",  
      "target-arrow-shape": "circle",  
      "target-arrow-color": "#6495ED",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002234  
  {  
    "selector": "edge[represents='RO:0002234']",  
    "style": {  
      "line-color": "#ED6495",  
      "line-style": "solid",  
      "target-arrow-shape": "circle",  
      "target-arrow-color": "#ED6495",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002407  
  {  
    "selector": "edge[represents='RO:0002407']",  
    "style": {  
      "line-color": "#FF0000",  
      "line-style": "dashed",  
      "target-arrow-shape": "tee",  
      "target-arrow-color": "#FF0000",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002409  
  {  
    "selector": "edge[represents='RO:0002409']",  
    "style": {  
      "line-color": "#008800",  
      "line-style": "dashed",  
      "target-arrow-shape": "triangle",  
      "target-arrow-color": "#008800",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0012006  
  {  
    "selector": "edge[represents='RO:0012006']",  
    "style": {  
      "line-color": "#FF0000",  
      "line-style": "solid",  
      "target-arrow-shape": "tee",  
      "target-arrow-color": "#FF0000",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0012005  
  {  
    "selector": "edge[represents='RO:0012005']",  
    "style": {  
      "line-color": "#008800",  
      "line-style": "solid",  
      "target-arrow-shape": "triangle",  
      "target-arrow-color": "#008800",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002212  
  {  
    "selector": "edge[represents='RO:0002212']",  
    "style": {  
      "line-color": "#FF0000",  
      "line-style": "dashed",  
      "target-arrow-shape": "tee",  
      "target-arrow-color": "#FF0000",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002213  
  {  
    "selector": "edge[represents='RO:0002213']",  
    "style": {  
      "line-color": "#008800",  
      "line-style": "dashed",  
      "target-arrow-shape": "triangle",  
      "target-arrow-color": "#008800",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0002413  
  {  
    "selector": "edge[represents='RO:0002413']",  
    "style": {  
      "line-color": "#800080",  
      "line-style": "solid",  
      "target-arrow-shape": "circle",  
      "target-arrow-color": "#800080",  
      "width": 5  
    }  
  },  
  
  # Edge represents mappings - RO:0012010  
  {  
    "selector": "edge[represents='RO:0012010']",  
    "style": {  
      "line-color": "#fF9999",  
      "line-style": "solid",  
      "target-arrow-shape": "square",  
      "target-arrow-color": "#fF9999",  
      "width": 5  
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
    styles = []

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


# # -------------------------------- Node Type Configuration --------------------------------
# # Node type configurations: maps type -> visual properties
# _NODE_TYPE_CONFIG = {
#     "gene":     {"shape": "ellipse",   "color": "#C8E6C9", "width": 50},
#     "complex":  {"shape": "rectangle", "color": "#E2BDE7", "width": 70},
#     "molecule": {"shape": "rectangle", "color": "#B2DFDB", "width": 60},
# }

# # -------------------------------- Edge Style Configuration --------------------------------
# EDGE_NAMES = {
#     'directly positively regulates': 'direct positive regulation/activation',
#     'directly negatively regulates': 'direct negative regulation/inhibition',
#     'indirectly positively regulates': 'indirect positive regulation',
#     'indirectly negatively regulates': 'indirect negative regulation',
#     'provides input for': 'provides input for',
#     'removes input for': 'removes input for',
#     'has input': 'input of',
#     'has output': 'has output',
#     'constitutively upstream of': 'constitutively upstream',
#     'causally upstream of, negative effect': 'upstream positive effect',
#     'causally upstream of, positive effect': 'upstream negative effect',
# }



# EDGE_STYLES = [
#     {
#         "selector": 'edge[interaction="directly positively regulates"]',
#         "style": {
#             "width": 3,
#             "line-color": "#008800",
#             "line-style": "solid",
#             "curve-style": "bezier",
#             "target-arrow-shape": "triangle",
#             "target-arrow-color": "#008800",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="directly negatively regulates"]',
#         "style": {
#             "width": 3,
#             "line-color": "#FF0000",
#             "line-style": "solid",
#             "curve-style": "bezier",
#             "target-arrow-shape": "tee",
#             "target-arrow-color": "#FF0000",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="indirectly positively regulates"]',
#         "style": {
#             "width": 3,
#             "line-color": "#008800",
#             "line-style": "dashed",
#             "curve-style": "bezier",
#             "target-arrow-shape": "triangle",
#             "target-arrow-color": "#008800",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="indirectly negatively regulates"]',
#         "style": {
#             "width": 3,
#             "line-color": "#FF0000",
#             "line-style": "dashed",
#             "curve-style": "bezier",
#             "target-arrow-shape": "tee",
#             "target-arrow-color": "#FF0000",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="provides input for"]',
#         "style": {
#             "width": 3,
#             "line-color": "#800080",
#             "line-style": "solid",
#             "curve-style": "bezier",
#             "target-arrow-shape": "diamond",
#             "target-arrow-color": "#800080",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="removes input for"]',
#         "style": {
#             "width": 3,
#             "line-color": "#FF9999",
#             "line-style": "solid",
#             "curve-style": "bezier",
#             "target-arrow-shape": "square",
#             "target-arrow-color": "#FF9999",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="has input"]',
#         "style": {
#             "width": 3,
#             "line-color": "#6495ED",
#             "line-style": "solid",
#             "curve-style": "bezier",
#             "target-arrow-shape": "none",
#             "source-arrow-shape": "circle",
#             "source-arrow-color": "#6495ED",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="has output"]',
#         "style": {
#             "width": 3,
#             "line-color": "#ED6495",
#             "line-style": "solid",
#             "curve-style": "bezier",
#             "target-arrow-shape": "circle",
#             "target-arrow-color": "#ED6495",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": "edge[interaction='constitutively upstream of']",
#         "style": {
#             "width": 3,
#             "line-color": "#95E095",
#             "line-style": "dashed",
#             "curve-style": "bezier",
#             "target-arrow-shape": "circle",
#             "target-arrow-color": "#95E095",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="causally upstream of, negative effect"]',
#         "style": {
#             "width": 3,
#             "line-color": "#95E095",
#             "line-style": "dashed",
#             "curve-style": "bezier",
#             "target-arrow-shape": "triangle",
#             "target-arrow-color": "#95E095",
#             "text-halign": "left",
#         }
#     },
#     {
#         "selector": 'edge[interaction="causally upstream of, positive effect"]',
#         "style": {
#             "width": 3,
#             "line-color": "#FF9999",
#             "line-style": "dashed",
#             "curve-style": "bezier",
#             "target-arrow-shape": "tee",
#             "target-arrow-color": "#FF9999",
#             "text-halign": "left",
#         }
#     }
# ]








#



# # ================================ Plot Interaction Type Legend =================================
# def plot_interaction_type_legend():
#     """Plot a legend for interaction types with alternating edge lines and labels."""
#     legend_elements = []
    
#     # First, add all the nodes (one pair per interaction type)
#     node_pairs = []
#     for i, edge_style in enumerate(EDGE_STYLES):
#         selector = edge_style['selector']
#         # Handle both single and double quotes in selector
#         if 'edge[interaction="' in selector:
#             interaction_type = selector.split('edge[interaction="')[1].split('"]')[0]
#         elif "edge[interaction='" in selector:
#             interaction_type = selector.split("edge[interaction='")[1].split("']")[0]
#         else:
#             continue  # Skip if selector doesn't match expected format
        
#         # Create source and target nodes for the edge line
#         source_id = f"legend_source_{i}"
#         target_id = f"legend_target_{i}"
#         # Create nodes for the label on the next row
#         label_source_id = f"legend_label_source_{i}"
#         label_target_id = f"legend_label_target_{i}"
        
#         node_pairs.append((source_id, target_id, label_source_id, label_target_id, interaction_type))
        
#         # Add nodes for edge line
#         legend_elements.append({
#             "data": {"id": source_id, "label": ""}
#         })
#         legend_elements.append({
#             "data": {"id": target_id, "label": ""}
#         })
#         # Add nodes for label line
#         legend_elements.append({
#             "data": {"id": label_source_id, "label": ""}
#         })
#         legend_elements.append({
#             "data": {"id": label_target_id, "label": EDGE_NAMES[interaction_type]}
#         })
    
#     # Then add all the edges (interaction lines only)
#     for i, (source_id, target_id, _, _, interaction_type) in enumerate(node_pairs):
#         legend_elements.append({
#             "data": {
#                 "id": f"legend_edge_{i}",
#                 "source": source_id,
#                 "target": target_id,
#                 "interaction": interaction_type,
#             }
#         })
    
#     # Create legend-specific stylesheet
#     legend_stylesheet = [
#         {
#             "selector": "node",
#             "style": {
#                 "opacity": 0,
#                 "width": 1,
#                 "height": 1
#             }
#         },
#         {
#             "selector": "node[label]",
#             "style": {
#                 "opacity": 1,
#                 "label": "data(label)",
#                 "text-halign": "left",
#                 "text-valign": "center",
#                 "color": THEME_COLOR,  # Adapts to Streamlit theme
#                 "font-size": "14px",
#                 "background-opacity": 0,
#                 "width": 1,
#                 "height": 1
#             }
#         },
#         {
#             "selector": "edge",
#             "style": {
#                 "width": 4,
#             }
#         }
#     ] + EDGE_STYLES
    
#     # Calculate positions: alternating rows for edges and labels
#     positions = {}
#     row_spacing = 35
#     for i, (source_id, target_id, label_source_id, label_target_id, _) in enumerate(node_pairs):
#         row_index = i * 2  # Each interaction takes 2 rows
#         # Edge line on even rows (left-aligned)
#         positions[source_id] = {"x": 2, "y": row_index * row_spacing + 20}
#         positions[target_id] = {"x": 150, "y": row_index * row_spacing + 20}
#         # Label on odd rows (left-aligned)
#         positions[label_source_id] = {"x": 2, "y": (row_index + 1) * row_spacing + 20}
#         positions[label_target_id] = {"x": 160, "y": (row_index + 1) * row_spacing + 20}
    
#     cytoscape(
#         elements=legend_elements,
#         stylesheet=legend_stylesheet,
#         layout={
#             "name": "preset",
#             "positions": positions,
#             "fit": True,
#             "padding": 4
#         },
#         height=f"{len(node_pairs) * 2 * row_spacing + 40}px",
#         key="legend",
#         user_panning_enabled=False,
#         user_zooming_enabled=False,
#         selection_type="none",
#     )


