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

# ============================ Functions ============================
def _FILE_READERS(handler: str, file_path: str | Path, **kwargs) -> pd.DataFrame:
    """Reads different types of table files and returns a pandas DataFrame."""
    match handler:
        case "tsv":
            return pd.read_csv(file_path, sep="\t", index_col=1, **kwargs)
        case "csv":
            return pd.read_csv(file_path, index_col=1, **kwargs)
        case "xlsx":
            return pd.read_excel(file_path, index_col=1, **kwargs)
        case _:
            raise ValueError(f"Unsupported file handler: {handler}")

def get_theme_aware_label_color() -> tuple[str, str]:
    """Get appropriate label color and background color based on Streamlit theme."""
    streamlit_theme = st.context.theme.type
    try:
        if streamlit_theme == "dark":
            # return white text on black background
            return ("#FFFFFF", "#000000")
        else:
            return ("#000000", "#FFFFFF")
    except Exception:
        return ("#000000", "#FFFFFF")