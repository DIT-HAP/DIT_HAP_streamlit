"""
Ontology Annotation Formatting
==============================

Convert PomBase phenotype (PHAF) and human-disease (MONDO GAF) annotation
tables into the GO-style GAF 2.2 format consumed by goatools enrichment.

Split out of the former src/preparation.py: this module holds the pure
data-formatting helpers, while the Streamlit input widgets moved to
src/ui/inputs.py.

Input
-----
- FYPO / MONDO .obo ontology files and their raw PomBase annotation tables.

Output
------
- GO-style .tsv files written next to the source annotation table, returned
  as a Path.

Author:   Yusheng Yang (guidance) + Claude (implementation)
Date:     2026-07-14
Version:  1.0.0
"""

# =============================================================================
# IMPORTS
# =============================================================================
# 1. Standard Library Imports
from pathlib import Path

# 2. Data Processing Imports
import pandas as pd

# 3. Third-party Imports
from goatools.obo_parser import GODag

# =============================================================================
# GAF 2.2 output column order (shared by both formatters)
# =============================================================================
GAF_COLUMNS = [
    "DB", "DB_Object_ID", "DB_Object_Symbol", "Qualifier", "GO_ID",
    "DB:Reference", "Evidence", "With", "Aspect", "DB_Object_Name",
    "Synonym", "DB_Object_Type", "Taxon", "Date", "Assigned_By",
    "Annotation_Extension", "Gene_Product_Form_ID",
]


# =============================================================================
# CORE LOGIC
# =============================================================================

def assign_term_name(term_ID: str, term_dag: GODag) -> str:
    """Return the ontology term name for an ID, or a placeholder if absent."""
    if term_ID in term_dag:
        return term_dag[term_ID].name
    return f"No record for {term_ID}"


def format_phaf_file(fypo_obo_file: Path, phaf_file: Path) -> Path:
    """Format the PHAF phenotype file into a GO-style GAF and return its path."""
    phaf_dag = GODag(str(fypo_obo_file))
    phaf = pd.read_csv(phaf_file, sep="\t").query(
        "(`Allele type` == 'deletion' or `Allele type` == 'disruption') "
        "and Condition.str.contains('FYECO:0000005')"
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
    reformat_phaf = phaf[GAF_COLUMNS].copy()

    out_path = phaf_file.parent / "phaf_go_style.tsv"
    with out_path.open("w") as f:
        f.write(
            "!gaf-version: 2.2\n!generated-by: Yusheng Yang\n"
            "!URL: https://www.pombase.org/monthly_releases/2025/pombase-2025-09-01/"
            "phenotypes_and_genotypes/pombase_phenotype_annotation.phaf.tsv\n"
            "!contact: yangyusheng@nibs.ac.cn\n"
        )
    reformat_phaf.to_csv(out_path, sep="\t", index=False, header=False, mode="a")
    return out_path


def format_mondo_gaf_file(mondo_obo_file: Path, mondo_gaf_file: Path) -> Path:
    """Format the MONDO disease GAF into a GO-style GAF and return its path."""
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
    reformat_mondo = mondo[GAF_COLUMNS].copy()

    out_path = mondo_gaf_file.parent / "mondo_go_style.tsv"
    with out_path.open("w") as f:
        f.write(
            "!gaf-version: 2.2\n!generated-by: Yusheng Yang\n"
            "!URL: https://www.pombase.org/monthly_releases/2025/pombase-2025-08-01/"
            "ontologies_and_associations/human_disease_association.tsv\n"
            "!contact: yangyusheng@nibs.ac.cn\n"
        )
    reformat_mondo.to_csv(out_path, sep="\t", index=False, header=False, mode="a")
    return out_path
