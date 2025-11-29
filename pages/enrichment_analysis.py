"""
Enrichment analysis page using the new modular data loading architecture.

This page provides gene ontology and phenotype enrichment analysis functionality.
"""

# ================================= Imports =================================
import streamlit as st
import sys
import pandas as pd

sys.path.append("../src")
from src.preparation import sidebar_gene_input
from src.data_config import get_default_config
from src.data_manager import load_gene_metadata, load_gene_level_stats, load_gene_ontology_data, load_gene_phenotype_data, load_disease_ontology_data
from src.enrichment_functions import background_configuration, ontology_enrichment_pipeline, stringdb_enrichment, display_enrichment_results

# ================================= Constants =================================
P_VALUE_THRESHOLD = 0.05

# ================================= Functions =================================

def load_enrichment_data():
    """Load only the data needed for enrichment analysis."""
    
    # Get default configuration
    config = get_default_config()
    
    # Validate configuration
    config.validate_all_paths()
    
    # Load only the required data categories
    with st.spinner("Loading gene metadata...", show_time=True):
        gene_metadata = load_gene_metadata(config.gene_metadata)

    with st.spinner("Loading gene level statistics...", show_time=True):
        gene_level = load_gene_level_stats(config.gene_level)
    
    with st.spinner("Loading ontology data...", show_time=True):
        gene_ontology_data = load_gene_ontology_data(config.gene_ontology_data)
    
    with st.spinner("Loading phenotype data...", show_time=True):
        gene_phenotype_data = load_gene_phenotype_data(config.gene_phenotype_data)
    
    with st.spinner("Loading disease ontology data...", show_time=True):
        disease_ontology_data = load_disease_ontology_data(config.mondo_disease_ontology_data)
    
    return gene_metadata, gene_level, gene_ontology_data, gene_phenotype_data, disease_ontology_data

def display_full_or_slim(res: pd.DataFrame, label: str, file_name: str, facet_layout: bool = False):
    """Streamlit layout for displaying full or slim results."""
    col1, col2 = st.columns([1,1])
    col1.success("Enrichment results found")
    col2.download_button(
        label=label,
        data=res.to_csv(index=False),
        file_name=file_name,
        mime="text/csv",
        on_click="ignore"
    )
    charts = display_enrichment_results(res)
    if facet_layout:
        chart_cols = st.columns(2)
        # Balance charts between columns based on number of terms
        # Assign each chart to the column with fewer total terms
        left_terms = 0
        right_terms = 0
        chart_assignments = []  # List of (column_index, chart_ns, chart_info)
        
        for chart_ns, chart_info in charts.items():
            n_terms = int(chart_info["n_terms"])
            if left_terms <= right_terms:
                chart_assignments.append((0, chart_ns, chart_info))
                left_terms += n_terms
            else:
                chart_assignments.append((1, chart_ns, chart_info))
                right_terms += n_terms
        
        # Display charts in their assigned columns
        for col_idx, chart_ns, chart_info in chart_assignments:
            with chart_cols[col_idx]:
                with st.container(border=True):
                    st.altair_chart(chart_info["chart"], width="stretch")  # type: ignore
    else:
        for chart_ns, chart_info in charts.items():
            with st.container(border=True):
                st.altair_chart(chart_info["chart"], width="stretch")  # type: ignore
def display_results(res: pd.DataFrame, res_slim: pd.DataFrame | None = None, ontology_name: str = "GO"):
    """Display enrichment results."""
    if res_slim is not None:
        full_col, slim_col = st.columns([1,1], border=True)
        with full_col:
            st.header(f":blue-background[{ontology_name} Enrichment Results (full)]", divider="blue")
            if res.empty:
                st.warning("No enrichment results found")
            else:
                display_full_or_slim(res, 
                                    f"Download {ontology_name} enrichment results (full)", 
                                    f"{ontology_name.lower()}_enrichment_results_full.csv"
                )
        with slim_col:
            st.header(f":green-background[{ontology_name} Enrichment Results (slim)]", divider="green")
            if res_slim.empty:
                st.warning("No enrichment results found (slim)")
            else:
                display_full_or_slim(res_slim,
                                    f"Download {ontology_name} enrichment results (slim)",
                                    f"{ontology_name.lower()}_enrichment_results_slim.csv"
                )
    else:
        st.header(f":blue-background[{ontology_name} Enrichment Results]", divider="blue")
        if res.empty:
            st.warning("No enrichment results found")
        else:
            display_full_or_slim(res, 
                                f"Download {ontology_name} enrichment results", 
                                f"{ontology_name.lower()}_enrichment_results.csv",
                                facet_layout=True
            )


def main():
    """Main entry point for the enrichment analysis page."""

    st.title(":bar_chart: *S. pombe* Enrichment Analysis")

    # Introduction and Usage Guide
    st.markdown("""
    ### 🔍 Functional Enrichment Analysis for DIT-HAP Pipeline Results

    This page provides **comprehensive functional enrichment analysis** for gene sets identified from the **[DIT-HAP pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)**.
    Discover biological meaning in your transposon insertion results through multiple ontology approaches.
    """)

    with st.expander("📖 How to Use This Tool", expanded=False):
        st.markdown("""
        **Step 1: Configure Background** (Main Page)
        - Choose background gene set for statistical comparison
        - Options: All genes, essential genes only, non-essential genes only
        - Set FDR threshold for significance testing (default: 0.05)

        **Step 2: Input Genes** (Sidebar)
        - Enter genes identified from DIT-HAP pipeline analysis
        - Use gene names (`cdc2`, `wee1`) or systematic IDs (`SPAC1002.09c`)
        - Separate multiple genes with commas or newlines
        - Click "Submit" to start analysis

        **Step 3: Review Results**
        - **GO Enrichment**: Gene Ontology biological processes, molecular functions
        - **FYPO Enrichment**: Fission yeast phenotype ontology analysis
        - **MONDO Enrichment**: Human disease ontology associations
        - **STRING Enrichment**: Protein-protein interaction network analysis

        **Step 4: Interpret Findings**
        - Compare significant terms across different ontologies
        - Download results for downstream analysis
        - Use enriched terms to generate biological hypotheses
        """)

    with st.expander("🔬 Enrichment Methods", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
                **🧬 Gene Ontology (GO) Enrichment**

                **What it tests**: Over-representation of biological functions in your gene set

                **Categories analyzed**:
                - **Biological Process (BP)**: Cellular processes and pathways
                - **Molecular Function (MF)**: Molecular activities and binding
                - **Cellular Component (CC)**: Cellular locations and structures

                **Statistical method**: Fisher's exact test with Benjamini-Hochberg FDR correction
                **Database source**: [Gene Ontology Consortium](http://geneontology.org/)
                **Best for**: Understanding general biological functions and pathways
                """)

            st.markdown("""
                **🧫 FYPO Enrichment**

                **What it tests**: Over-representation of phenotypic characteristics in *S. pombe*

                **Categories analyzed**:
                - **Growth phenotypes**: Colony size, growth rate, morphology
                - **Cell cycle**: Mitosis, meiosis, cytokinesis defects
                - **Stress responses**: Environmental, chemical, genetic stresses
                - **Metabolism**: Nutrient utilization, biosynthetic pathways

                **Statistical method**: Fisher's exact test with Benjamini-Hochberg FDR correction
                **Database source**: [FYPO Ontology](https://github.com/pombase/fypo)
                **Best for**: Yeast-specific phenotypic interpretations
                """)

        with col2:
            st.markdown("""
                **🏥 MONDO Disease Enrichment**

                **What it tests**: Over-representation of human disease associations

                **Categories analyzed**:
                - **Genetic diseases**: Inherited disorders and syndromes
                - **Complex diseases**: Cancer, neurodegeneration, metabolic disorders
                - **Molecular mechanisms**: Pathway conservation across species
                - **Therapeutic targets**: Drug discovery and validation insights

                **Statistical method**: Fisher's exact test with Benjamini-Hochberg FDR correction
                **Database source**: [MONDO Disease Ontology](https://github.com/mondo-initiative/mondo)
                **Best for**: Translational research and medical relevance
                """)

            st.markdown("""
                **🕸️ STRING Enrichment**

                **What it tests**: Enrichment of protein-protein interaction networks

                **Network metrics**:
                - **Protein interactions**: Physical and functional associations
                - **Pathway enrichment**: KEGG, Reactome, BioCyc pathways
                - **Domain analysis**: Pfam, InterPro protein domains
                - **Co-expression**: Gene co-regulation and expression patterns

                **Statistical method**: Hypergeometric test with multiple testing correction
                **Database source**: [STRING Database](https://string-db.org/)
                **Best for**: Understanding molecular interactions and networks
                """)

    with st.expander("🎯 Analysis Guidelines", expanded=False):
        st.markdown("""
        **Gene Selection Strategy:**
        - **Essential genes**: From depletion analysis (strong negative fitness)
        - **Clustered genes**: From feature space analysis (similar statistical profiles)
        - **Condition-specific genes**: Genes responding to particular experimental conditions
        - **Pathway candidates**: Genes with related functional annotations

        **Interpreting Results:**
        - **Lower p-values**: More statistically significant enrichment
        - **Higher fold enrichment**: Stronger over-representation
        - **FDR < 0.05**: Generally considered significant after correction
        - **Consistent patterns**: Same biological theme across multiple ontologies

        **Quality Considerations:**
        - **Background set selection**: Critical for valid statistical comparison
        - **Gene set size**: Too few genes reduce statistical power
        - **Multiple testing**: FDR correction accounts for multiple comparisons
        - **Biological validation**: Cross-check with literature and experimental evidence
        """)

    with st.expander("📊 Understanding Output", expanded=False):
        st.markdown("""
        **Result Tables Include:**
        - **Term ID**: Ontology identifier (e.g., `GO:0007049`, `FYPO:0000015`)
        - **Term Name**: Human-readable description of biological concept
        - **p-value**: Raw statistical significance from enrichment test
        - **FDR/q-value**: Multiple testing corrected significance
        - **Fold Enrichment**: How much more common than expected by chance
        - **Genes in Term**: How many of your genes are annotated to this term
        - **Background Genes**: Total genes with this annotation in background
        - **List of Genes**: Which of your specific genes contribute to enrichment

        **Visualizations:**
        - **Bar charts**: Top enriched terms by statistical significance
        - **Scatter plots**: Enrichment significance vs. term specificity
        - **Interactive charts**: Hover for detailed term information
        - **Color coding**: Different significance levels and categories
        """)

    with st.expander("⚙️ Technical Details", expanded=False):
        st.markdown("""
        **Statistical Methods:**
        - **Fisher's Exact Test**: For GO, FYPO, and MONDO enrichment
        - **Hypergeometric Test**: For STRING protein interaction enrichment
        - **Benjamini-Hochberg Procedure**: False Discovery Rate correction
        - **Multiple Relationships**: `is_a` and `part_of` ontology relationships

        **Data Sources:**
        - **GO**: Gene Ontology Consortium (current monthly release)
        - **FYPO**: PomBase phenotype annotations (fission yeast specific)
        - **MONDO**: Human disease ontology cross-species mappings
        - **STRING**: Protein interaction networks (experimental + computational)

        **Performance Considerations:**
        - **Caching**: Ontology data cached for faster repeated analyses
        - **Parallel processing**: Multiple ontologies analyzed simultaneously
        - **Memory optimization**: Efficient data structures for large gene sets
        - **Background selection**: Pre-computed gene sets for common comparisons
        """)

    with st.expander("🔗 Integration with DIT-HAP Pipeline", expanded=False):
        st.markdown("""
        **Input from Pipeline:**
        - **Essential genes**: Genes showing strong depletion in time course analysis
        - **Fitness clusters**: Genes with similar depletion profiles from feature space
        - **Conditional hits**: Genes essential under specific experimental conditions
        - **Quality filtered genes**: High-confidence identifications from pipeline QC

        **Complementary to Other Analyses:**
        - **Depletion curves**: Identify which genes to test for functional enrichment
        - **Feature space**: Discover gene clusters with shared functional properties
        - **Genome browser**: Visualize genomic context for significant genes
        - **Network analysis**: Extend with protein-protein interaction data

        **Biological Interpretation:**
        - **Pathway discovery**: Identify affected biological processes
        - **Phenotype prediction**: Anticipate cellular effects of gene disruption
        - **Drug target validation**: Assess therapeutic potential of essential genes
        - **Evolutionary conservation**: Compare findings across model organisms
        """)

    st.markdown("---")

    # Load required data
    gene_metadata, gene_level, gene_ontology_data, gene_phenotype_data, disease_ontology_data = load_enrichment_data()
    
    # Enrichment configuration
    with st.container(border=True):
        st.header(":gear: Enrichment Configuration")

        # Configure background genes
        bg_genes = background_configuration(
            gene_level,
            gene_metadata
        )

        # FDR threshold
        with st.expander("Advanced settings", expanded=False):
            with st.container(border=True):
                fdr_threshold = st.number_input(
                    "FDR threshold for significance:",
                    min_value=0.0,
                    max_value=1.0,
                    value=P_VALUE_THRESHOLD,
                    step=0.01,
                    help="False Discovery Rate (FDR) threshold for determining significant enrichment results."
                )

    # Get gene input from sidebar
    covered_gene_sysIDs, submit_button = sidebar_gene_input(
        gene_metadata.gene_info_with_essentiality, 
        gene_level.gene_level_LFCs,
        bg_genes
    )

    # Perform enrichment analysis if genes are submitted
    with st.container(border=True):
        st.header(":mag: Enrichment Analysis Results", divider="gray")

        if submit_button and covered_gene_sysIDs:

            # display the enrichment input and parameters
            st.caption(f"Enrichment analysis performed on :green[__{len(covered_gene_sysIDs)}__] query genes against a background of :blue[__{len(bg_genes)}__] genes.")
            st.caption(f"FDR threshold set to :red[__{fdr_threshold}__].")

            ontology_tab = st.tabs(["GO enrichment", "FYPO enrichment", "Mondo enrichment", "STRING enrichment"])
            with ontology_tab[0]:
                with st.spinner("Performing GO enrichment analysis..."):

                    load_kwargs = {
                        "relationships": {"is_a", "part_of"},
                        "propagate_counts": True,
                        "load_obsolete": False
                    }
                    enrichment_kwargs = {
                        "alpha": fdr_threshold,
                        "methods": ["fdr_bh"],
                        "propagate_counts": True,
                        "relationships": {"is_a", "part_of"},
                        "prt": None,
                    }

                    format_kwargs = {
                        "itemid2name": gene_metadata.id2name
                    }

                    res, res_slim = ontology_enrichment_pipeline(gene_ontology_data, covered_gene_sysIDs, bg_genes, load_kwargs=load_kwargs, enrichment_kwargs=enrichment_kwargs, format_kwargs=format_kwargs)
                    display_results(res, res_slim, ontology_name="GO")
            with ontology_tab[1]:
                with st.spinner("Performing FYPO enrichment analysis..."):

                    load_kwargs = {
                        "propagate_counts": True,
                        "load_obsolete": False
                    }

                    enrichment_kwargs = {
                        "alpha": fdr_threshold,
                        "methods": ["fdr_bh"],
                        "propagate_counts": True,
                        "prt": None,
                    }

                    format_kwargs = {
                        "itemid2name": gene_metadata.id2name
                    }

                    res, res_slim = ontology_enrichment_pipeline(gene_phenotype_data, covered_gene_sysIDs, bg_genes, load_kwargs=load_kwargs, enrichment_kwargs=enrichment_kwargs, format_kwargs=format_kwargs)
                    display_results(res, res_slim, ontology_name="FYPO")
            with ontology_tab[2]:
                with st.spinner("Performing Mondo enrichment analysis..."):

                    load_kwargs = {
                        "propagate_counts": True,
                        "load_obsolete": False
                    }

                    enrichment_kwargs = {
                        "alpha": fdr_threshold,
                        "methods": ["fdr_bh"],
                        "propagate_counts": True,
                        "prt": None,
                    }

                    format_kwargs = {
                        "itemid2name": gene_metadata.id2name
                    }
                    res, res_slim = ontology_enrichment_pipeline(disease_ontology_data, covered_gene_sysIDs, bg_genes, load_kwargs=load_kwargs, enrichment_kwargs=enrichment_kwargs, format_kwargs=format_kwargs)
                    display_results(res, res_slim, ontology_name="Mondo")
            with ontology_tab[3]:
                with st.spinner("Performing STRING enrichment analysis..."):
                    res = stringdb_enrichment(covered_gene_sysIDs, bg_genes)
                    display_results(res, ontology_name="STRING")
        else:
            st.warning("Please input query genes for enrichment analysis")


if __name__ == "__main__":
    main()