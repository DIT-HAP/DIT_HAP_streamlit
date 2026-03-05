"""
This script prepares the data for the gene page.
"""

# ================================= Imports =================================
import pandas as pd
import streamlit as st
from pathlib import Path
from goatools.obo_parser import GODag
from datetime import date

# ================================= Functions =================================

def get_gene_list_from_query(text: str) -> list[str]:
    """Parse gene list from text input."""
    if not text.strip():
        return []
    
    # Split by commas, newlines, or spaces
    genes = []
    for separator in [',', '\n', ' ']:
        if separator in text:
            genes = [g.strip() for g in text.split(separator) if g.strip()]
            break
    
    return genes

def validate_gene_ids(genes: list[str], gene_info: pd.DataFrame, bg_genes: set[str]) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """Validate gene list against available data."""

    name2sysID = dict(zip(gene_info["gene_name"], gene_info["gene_systematic_id"]))
    sysID2name = dict(zip(gene_info["gene_systematic_id"], gene_info["gene_name"]))
 
    valid_genes = []
    invalid_genes = []

    covered_sysIDs = bg_genes
    covered_names = set([sysID2name[sysID] if sysID in sysID2name else sysID for sysID in covered_sysIDs]) 
    covered_genes = []
    covered_gene_sysIDs = []
    uncovered_genes = []

    # if the gene is a name, convert it to sysID
    for gene in genes:
        if gene in name2sysID.keys():
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
    column_layout: bool = True
) -> list[str]:
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

    gene_input = form_container.text_area("(comma or newline separated)", value="SPAC1002.09c\nSPAC3G9.12", height=height)
    gene_ids = get_gene_list_from_query(gene_input)
    valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes = validate_gene_ids(gene_ids, gene_info_with_essentiality, default_bg_genes)
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

def sidebar_gene_input(gene_info_with_essentiality: pd.DataFrame, gene_level_LFCs: pd.DataFrame, bg_genes: set[str] | None = None) -> tuple[list[str] | None, bool]:
    """Set the sidebar for the plot page."""

    if bg_genes is None:
        bg_genes = set(gene_level_LFCs.index.tolist())

    input_form = st.sidebar.form("gene_input", clear_on_submit=False, border=True)
    input_form.subheader("Enter query genes:")
    gene_input = input_form.text_area("(comma or newline separated)", value="SPAC1002.09c\nSPAC3G9.12", height=300)
    submit_button = input_form.form_submit_button("Submit")
    if submit_button:
        gene_ids = get_gene_list_from_query(gene_input)
        valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes = validate_gene_ids(gene_ids, gene_info_with_essentiality, bg_genes)
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
    existing_groups: list[dict] | None = None
) -> tuple[dict | None, bool, bool]:
    """
    Sidebar input for adding gene groups to feature space visualization.
    
    Args:
        gene_info_with_essentiality: DataFrame with gene information
        gene_level_LFCs: DataFrame with gene level statistics
        bg_genes: Set of background genes (default: all genes in gene_level_LFCs)
        existing_groups: List of existing group dictionaries to check for duplicate names
    
    Returns:
        tuple: (group_data dict or None, add_button_clicked bool, clear_button_clicked bool)
        group_data structure: {"name": str, "genes": list[str], "color": str}
    """
    # Default color palette for groups
    default_color_palette = [
        "#e41a1c",  # Red
        "#377eb8",  # Blue
        "#4daf4a",  # Green
        "#984ea3",  # Purple
        "#ff7f00",  # Orange
        "#ffff33",  # Yellow
        "#a65628",  # Brown
        "#f781bf",  # Pink
    ]
    
    if bg_genes is None:
        bg_genes = set(gene_level_LFCs.index.tolist())
    
    if existing_groups is None:
        existing_groups = []
    
    # Initialize session state for group counter if not exists
    if "group_counter" not in st.session_state:
        st.session_state.group_counter = len(existing_groups) + 1
    
    # Generate default group name
    default_name = f"Group {st.session_state.group_counter}"
    
    # Calculate default color based on current group count
    default_color = default_color_palette[len(existing_groups) % len(default_color_palette)]
    
    # Initialize session state for current group name if not exists
    if "current_group_name" not in st.session_state:
        st.session_state.current_group_name = default_name
    
    # Create form for group input
    input_form = st.sidebar.form("gene_group_input", clear_on_submit=True, border=True)
    input_form.subheader("Add Gene Group:")
    
    # Group name input - use session state to preserve the value
    group_name = input_form.text_input(
        "Group name",
        value=st.session_state.current_group_name,
        help="Enter a descriptive name for this gene group",
        key="group_name_widget"
    )
    
    # Update session state with the entered name
    st.session_state.current_group_name = group_name
    
    # Color picker input - use session state to preserve the selected color
    if "current_group_color" not in st.session_state:
        st.session_state.current_group_color = default_color
    
    group_color = input_form.color_picker(
        "Group color",
        value=st.session_state.current_group_color,
        help="Select a color for this group (default: next color in palette)",
        key="color_picker_widget"
    )
    
    # Update session state with the selected color
    st.session_state.current_group_color = group_color
    
    # Gene list input
    gene_input = input_form.text_area(
        "Genes (comma or newline separated)",
        value="",
        height=200,
        help="Enter gene names or systematic IDs"
    )
    
    # Buttons
    col1, col2 = input_form.columns(2)
    add_button = col1.form_submit_button("Add Group", type="primary")
    clear_button = col2.form_submit_button("Clear All", type="secondary")
    
    group_data = None
    
    if add_button:
        # Parse and validate genes
        gene_ids = get_gene_list_from_query(gene_input)
        
        if not gene_ids:
            st.sidebar.warning("⚠️ Please enter at least one gene")
            return None, True, False
        
        if not group_name.strip():
            st.sidebar.warning("⚠️ Please enter a group name")
            return None, True, False
        
        # Check for duplicate group name
        existing_names = [g["name"] for g in existing_groups]
        if group_name.strip() in existing_names:
            st.sidebar.warning(f"⚠️ Group name '{group_name}' already exists. Please use a different name.")
            return None, True, False
        
        # Validate genes
        valid_genes, invalid_genes, covered_genes, covered_gene_sysIDs, uncovered_genes = validate_gene_ids(
            gene_ids, gene_info_with_essentiality, bg_genes
        )
        
        # Show validation badges
        input_form.badge(f"{len(gene_ids)} genes submitted", icon=":material/arrow_right_alt:", color="gray")
        input_form.badge(f"{len(valid_genes)} valid genes", icon=":material/check:", color="green")
        input_form.badge(f"{len(invalid_genes)} invalid genes", icon=":material/close:", color="red")
        input_form.badge(f"{len(covered_genes)} covered genes", icon=":material/check_circle:", color="blue")
        input_form.badge(f"{len(uncovered_genes)} uncovered genes", icon=":material/error:", color="orange")
        
        # Show invalid/uncovered genes if any
        if invalid_genes:
            with st.sidebar.expander("Invalid genes", expanded=False):
                st.text("\n".join(invalid_genes))
        
        if uncovered_genes:
            with st.sidebar.expander("Uncovered genes", expanded=False):
                st.text("\n".join(uncovered_genes))
        
        # Only add group if there are covered genes
        if covered_gene_sysIDs:
            # Use the name and color from session state
            selected_name = st.session_state.current_group_name
            selected_color = st.session_state.current_group_color
            group_data = {
                "name": selected_name.strip(),
                "genes": covered_gene_sysIDs,
                "color": selected_color
            }
            # Increment group counter for next default name
            st.session_state.group_counter += 1
            # Reset name and color to default for next group
            next_default_name = f"Group {st.session_state.group_counter}"
            next_default_color = default_color_palette[len(existing_groups) % len(default_color_palette)]
            st.session_state.current_group_name = next_default_name
            st.session_state.current_group_color = next_default_color
            st.sidebar.success(f"✅ Group '{selected_name}' added with {len(covered_gene_sysIDs)} genes")
        else:
            st.sidebar.warning("⚠️ No valid covered genes found. Group not added.")
        
        return group_data, True, False
    
    if clear_button:
        return None, False, True
    
    return None, False, False

def assign_term_name(term_ID, term_dag):
    if term_ID in term_dag:
        return term_dag[term_ID].name
    else:
        return "No record for {}".format(term_ID)

def format_phaf_file(fypo_obo_file: Path, phaf_file: Path) -> Path:
    """Format the phaf file to the go style gaf file."""
    phaf_dag = GODag(str(fypo_obo_file))
    phaf = pd.read_csv(
        phaf_file, sep="\t"
    ).query(
        "(`Allele type` == 'deletion' or `Allele type` == 'disruption') and Condition.str.contains('FYECO:0000005')"
    )
    phaf["DB"] = "PomBase"
    phaf["DB_Object_ID"] = phaf["Gene systematic ID"]
    phaf["DB_Object_Symbol"] = phaf["Gene symbol"]
    phaf["Qualifier"] = ""
    phaf["GO_ID"] = phaf["FYPO ID"]
    phaf["DB:Reference"] = phaf["Reference"]
    phaf["Evidence"] = phaf["Evidence"]
    phaf["With"] = ""
    phaf["Aspect"] = "FYPO"
    phaf["DB_Object_Name"] = phaf["FYPO ID"].apply(assign_term_name, term_dag=phaf_dag)
    phaf["Synonym"] = ""
    phaf["DB_Object_Type"] = "protein"
    phaf["Taxon"] = "taxon:4896"
    phaf["Date"] = phaf["Date"].str.replace("-", "")
    phaf["Assigned_By"] = phaf["#Database name"]
    phaf["Annotation_Extension"] = phaf["Extension"]
    phaf["Gene_Product_Form_ID"] = ""
    reformat_phaf = phaf[["DB", "DB_Object_ID", "DB_Object_Symbol", "Qualifier", "GO_ID", "DB:Reference", "Evidence", "With", "Aspect",
             "DB_Object_Name", "Synonym", "DB_Object_Type", "Taxon", "Date", "Assigned_By", "Annotation_Extension", "Gene_Product_Form_ID"]].copy()

    with open(phaf_file.parent / "phaf_go_style.tsv", "w") as f:
        f.write(f"!gaf-version: 2.2\n!generated-by: Yusheng Yang\n!URL: https://www.pombase.org/monthly_releases/2025/pombase-2025-09-01/phenotypes_and_genotypes/pombase_phenotype_annotation.phaf.tsv\n!contact: yangyusheng@nibs.ac.cn\n")
    
    reformat_phaf.to_csv(phaf_file.parent / "phaf_go_style.tsv", sep="\t", index=False, header=False, mode="a")

    return phaf_file.parent / "phaf_go_style.tsv"

def format_mondo_gaf_file(mondo_obo_file: Path, mondo_gaf_file: Path) -> Path:
    """Format the mondo gaf file to the go style gaf file."""
    mondo_dag = GODag(str(mondo_obo_file))
    mondo = pd.read_csv(mondo_gaf_file, sep="\t")
    mondo["DB"] = "Pombase"
    mondo["DB_Object_ID"] = mondo["#gene_systematic_id"]
    mondo["DB_Object_Symbol"] = mondo["gene_name"]
    mondo["Qualifier"] = ""
    mondo["GO_ID"] = mondo["mondo_id"]
    mondo["DB:Reference"] = mondo["reference"]
    mondo["Evidence"] = ""
    mondo["With"] = ""
    mondo["Aspect"] = "MONDO"
    mondo["DB_Object_Name"] = mondo["mondo_id"].apply(assign_term_name, term_dag=mondo_dag)
    mondo["Synonym"] = ""
    mondo["DB_Object_Type"] = "protein"
    mondo["Taxon"] = "taxon:4896"
    mondo["Date"] = mondo["date"].fillna("2025-09-01").str.replace("-", "")
    mondo["Assigned_By"] = "PomBase"
    mondo["Annotation_Extension"] = ""
    mondo["Gene_Product_Form_ID"] = ""
    reformat_mondo = mondo[["DB", "DB_Object_ID", "DB_Object_Symbol", "Qualifier", "GO_ID", "DB:Reference", "Evidence", "With", "Aspect",
             "DB_Object_Name", "Synonym", "DB_Object_Type", "Taxon", "Date", "Assigned_By", "Annotation_Extension", "Gene_Product_Form_ID"]].copy()

    with open(mondo_gaf_file.parent / "mondo_go_style.tsv", "w") as f:
        f.write(f"!gaf-version: 2.2\n!generated-by: Yusheng Yang\n!URL: https://www.pombase.org/monthly_releases/2025/pombase-2025-08-01/ontologies_and_associations/human_disease_association.tsv\n!contact: yangyusheng@nibs.ac.cn\n")
    
    reformat_mondo.to_csv(mondo_gaf_file.parent / "mondo_go_style.tsv", sep="\t", index=False, header=False, mode="a")

    return mondo_gaf_file.parent / "mondo_go_style.tsv"