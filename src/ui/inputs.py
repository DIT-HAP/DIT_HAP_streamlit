"""
Gene Input Widgets
==================

Streamlit sidebar / form widgets for entering, parsing, and validating gene
queries against the available dataset. Split out of the former
src/preparation.py, which mixed these UI components with data formatting.

Input
-----
- Gene metadata / gene-level DataFrames used to validate submitted gene IDs.

Output
------
- Lists of validated systematic IDs (and group dicts) driving the pages.

Author:   Yusheng Yang (guidance) + Claude (implementation)
Date:     2026-07-14
Version:  1.0.0
"""

# =============================================================================
# IMPORTS
# =============================================================================
# 1. Standard Library Imports
# (none)

# 2. Data Processing Imports
import pandas as pd

# 3. Third-party Imports
import streamlit as st

# =============================================================================
# GLOBAL CONSTANTS
# =============================================================================
DEFAULT_GENE_QUERY = "SPAC1002.09c\nSPAC3G9.12"

# Default color palette for feature-space gene groups.
GROUP_COLOR_PALETTE = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
    "#ff7f00", "#ffff33", "#a65628", "#f781bf",
]


# =============================================================================
# CORE LOGIC
# =============================================================================

def get_gene_list_from_query(text: str) -> list[str]:
    """Parse a gene list from free text (comma-, newline-, or space-separated)."""
    if not text.strip():
        return []
    for separator in [",", "\n", " "]:
        if separator in text:
            return [g.strip() for g in text.split(separator) if g.strip()]
    return []


def validate_gene_ids(
    genes: list[str], gene_info: pd.DataFrame, bg_genes: set[str]
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """Split submitted genes into valid/invalid and covered/uncovered buckets."""
    name2sysID = dict(zip(gene_info["gene_name"], gene_info["gene_systematic_id"]))
    sysID2name = dict(zip(gene_info["gene_systematic_id"], gene_info["gene_name"]))

    valid_genes: list[str] = []
    invalid_genes: list[str] = []
    covered_sysIDs = bg_genes
    covered_names = {sysID2name.get(sysID, sysID) for sysID in covered_sysIDs}
    covered_genes: list[str] = []
    covered_gene_sysIDs: list[str] = []
    uncovered_genes: list[str] = []

    for gene in genes:
        if gene in name2sysID:
            valid_genes.append(gene)
            if gene in covered_names:
                covered_genes.append(gene)
                covered_gene_sysIDs.append(name2sysID[gene])
            else:
                uncovered_genes.append(gene)
        elif gene in name2sysID.values():
            valid_genes.append(gene)
            if gene in covered_sysIDs:
                covered_genes.append(gene)
                covered_gene_sysIDs.append(gene)
            else:
                uncovered_genes.append(gene)
        else:
            invalid_genes.append(gene)

    return valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes


def gene_input_form(
    input_form: st.container,
    gene_info_with_essentiality: pd.DataFrame,
    form_header: str,
    bg_genes: set[str] | None = None,
    height: int = 300,
    column_layout: bool = True,
) -> list[str]:
    """Render an inline gene-input form and return the covered systematic IDs."""
    if bg_genes is None:
        default_bg_genes = set(gene_info_with_essentiality["gene_systematic_id"].tolist())
    input_form.subheader(form_header)

    if column_layout:
        col1, col2 = input_form.columns(2)
        form_container = col1
        badge_container = col2
    else:
        form_container = input_form
        badge_container = input_form

    gene_input = form_container.text_area(
        "(comma or newline separated)", value=DEFAULT_GENE_QUERY, height=height
    )
    gene_ids = get_gene_list_from_query(gene_input)
    valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes = validate_gene_ids(
        gene_ids, gene_info_with_essentiality, default_bg_genes
    )
    badge_container.badge(f"{len(gene_ids)} genes submitted", icon=":material/arrow_right_alt:", color="gray")
    badge_container.badge(f"{len(valid_genes)} valid genes", icon=":material/check:", color="green")
    badge_container.badge(f"{len(invalid_genes)} invalid genes", icon=":material/close:", color="red")
    if bg_genes:
        badge_container.badge(f"{len(covered_genes)} covered genes", icon=":material/check_circle:", color="blue")
        badge_container.badge(f"{len(uncovered_genes)} uncovered genes", icon=":material/error:", color="orange")

    if invalid_genes:
        with badge_container.expander("Invalid genes", expanded=False):
            st.text("\n".join(invalid_genes))

    return covered_gene_sysIDs


def sidebar_gene_input(
    gene_info_with_essentiality: pd.DataFrame,
    gene_level_LFCs: pd.DataFrame,
    bg_genes: set[str] | None = None,
) -> tuple[list[str] | None, bool]:
    """Render the sidebar gene-query form and return covered IDs + submit state."""
    if bg_genes is None:
        bg_genes = set(gene_level_LFCs.index.tolist())

    input_form = st.sidebar.form("gene_input", clear_on_submit=False, border=True)
    input_form.subheader("Enter query genes:")
    gene_input = input_form.text_area("(comma or newline separated)", value=DEFAULT_GENE_QUERY, height=300)
    submit_button = input_form.form_submit_button("Submit")
    if submit_button:
        gene_ids = get_gene_list_from_query(gene_input)
        valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes = validate_gene_ids(
            gene_ids, gene_info_with_essentiality, bg_genes
        )
        input_form.badge(f"{len(gene_ids)} genes submitted", icon=":material/arrow_right_alt:", color="gray")
        input_form.badge(f"{len(valid_genes)} valid genes", icon=":material/check:", color="green")
        input_form.badge(f"{len(invalid_genes)} invalid genes", icon=":material/close:", color="red")
        input_form.badge(f"{len(covered_genes)} covered genes", icon=":material/check_circle:", color="blue")
        input_form.badge(f"{len(uncovered_genes)} uncovered genes", icon=":material/error:", color="orange")

        if invalid_genes:
            with st.sidebar.expander("Invalid genes", expanded=False):
                st.text("\n".join(invalid_genes))
        if uncovered_genes:
            with st.sidebar.expander("Uncovered genes", expanded=False):
                st.text("\n".join(uncovered_genes))
    else:
        covered_gene_sysIDs = None

    return covered_gene_sysIDs, submit_button


def sidebar_gene_group_input(
    gene_info_with_essentiality: pd.DataFrame,
    gene_level_LFCs: pd.DataFrame,
    bg_genes: set[str] | None = None,
    existing_groups: list[dict] | None = None,
) -> tuple[dict | None, bool, bool]:
    """Sidebar form to add a named gene group; returns (group, added, cleared)."""
    if bg_genes is None:
        bg_genes = set(gene_level_LFCs.index.tolist())
    if existing_groups is None:
        existing_groups = []

    if "group_counter" not in st.session_state:
        st.session_state.group_counter = len(existing_groups) + 1
    default_name = f"Group {st.session_state.group_counter}"
    default_color = GROUP_COLOR_PALETTE[len(existing_groups) % len(GROUP_COLOR_PALETTE)]
    if "current_group_name" not in st.session_state:
        st.session_state.current_group_name = default_name

    input_form = st.sidebar.form("gene_group_input", clear_on_submit=True, border=True)
    input_form.subheader("Add Gene Group:")
    group_name = input_form.text_input(
        "Group name",
        value=st.session_state.current_group_name,
        help="Enter a descriptive name for this gene group",
        key="group_name_widget",
    )
    st.session_state.current_group_name = group_name

    if "current_group_color" not in st.session_state:
        st.session_state.current_group_color = default_color
    group_color = input_form.color_picker(
        "Group color",
        value=st.session_state.current_group_color,
        help="Select a color for this group (default: next color in palette)",
        key="color_picker_widget",
    )
    st.session_state.current_group_color = group_color

    gene_input = input_form.text_area(
        "Genes (comma or newline separated)", value="", height=200,
        help="Enter gene names or systematic IDs",
    )
    col1, col2 = input_form.columns(2)
    add_button = col1.form_submit_button("Add Group", type="primary")
    clear_button = col2.form_submit_button("Clear All", type="secondary")

    if add_button:
        return _handle_group_add(
            gene_input, group_name, input_form, gene_info_with_essentiality,
            bg_genes, existing_groups,
        )
    if clear_button:
        return None, False, True
    return None, False, False


def _handle_group_add(
    gene_input: str,
    group_name: str,
    input_form: st.container,
    gene_info_with_essentiality: pd.DataFrame,
    bg_genes: set[str],
    existing_groups: list[dict],
) -> tuple[dict | None, bool, bool]:
    """Validate a submitted group and return (group_data, added=True, cleared=False)."""
    gene_ids = get_gene_list_from_query(gene_input)
    if not gene_ids:
        st.sidebar.warning("⚠️ Please enter at least one gene")
        return None, True, False
    if not group_name.strip():
        st.sidebar.warning("⚠️ Please enter a group name")
        return None, True, False
    if group_name.strip() in [g["name"] for g in existing_groups]:
        st.sidebar.warning(f"⚠️ Group name '{group_name}' already exists. Please use a different name.")
        return None, True, False

    valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes = validate_gene_ids(
        gene_ids, gene_info_with_essentiality, bg_genes
    )
    input_form.badge(f"{len(gene_ids)} genes submitted", icon=":material/arrow_right_alt:", color="gray")
    input_form.badge(f"{len(valid_genes)} valid genes", icon=":material/check:", color="green")
    input_form.badge(f"{len(invalid_genes)} invalid genes", icon=":material/close:", color="red")
    input_form.badge(f"{len(covered_genes)} covered genes", icon=":material/check_circle:", color="blue")
    input_form.badge(f"{len(uncovered_genes)} uncovered genes", icon=":material/error:", color="orange")

    if invalid_genes:
        with st.sidebar.expander("Invalid genes", expanded=False):
            st.text("\n".join(invalid_genes))
    if uncovered_genes:
        with st.sidebar.expander("Uncovered genes", expanded=False):
            st.text("\n".join(uncovered_genes))

    if not covered_gene_sysIDs:
        st.sidebar.warning("⚠️ No valid covered genes found. Group not added.")
        return None, True, False

    selected_name = st.session_state.current_group_name
    selected_color = st.session_state.current_group_color
    group_data = {"name": selected_name.strip(), "genes": covered_gene_sysIDs, "color": selected_color}
    st.session_state.group_counter += 1
    st.session_state.current_group_name = f"Group {st.session_state.group_counter}"
    st.session_state.current_group_color = GROUP_COLOR_PALETTE[len(existing_groups) % len(GROUP_COLOR_PALETTE)]
    st.sidebar.success(f"✅ Group '{selected_name}' added with {len(covered_gene_sysIDs)} genes")
    return group_data, True, False
