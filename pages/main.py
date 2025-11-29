"""
Main page for DIT-HAP Streamlit application.

This page provides a comprehensive introduction to the DIT-HAP visualization tool,
including scientific background, pipeline integration, and user guidance.
"""

import streamlit as st

# Main page content
def show_main_page():
    # Application Header
    st.title("🧬 DIT-HAP Streamlit Visualization")
    st.markdown("### Interactive Visualization and Analysis for DIT-HAP Pipeline Results")
    st.markdown("_A comprehensive web application for visualizing transposon insertion sequencing data and analyzing gene essentiality from the DIT-HAP pipeline_")

    st.markdown("---")

    # About Section
    st.header("🔬 About DIT-HAP Visualization")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **DIT-HAP Streamlit** is the visualization and analysis component for the **[DIT-HAP pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)** - a comprehensive bioinformatics workflow for diploid transposon mutagenesis and haploid fitness analysis.

        **Key Features:**
        - **Interactive gene visualization**: Explore gene depletion curves and insertion patterns from DIT-HAP pipeline outputs
        - **Feature space analysis**: Visualize genes in multidimensional feature space using pipeline-generated statistics
        - **Enrichment analysis**: Gene Ontology, FYPO, and disease ontology enrichment for pipeline results
        - **Real-time data exploration**: Dynamic filtering and selection of genes from pipeline datasets

        This application reads structured outputs from the DIT-HAP Snakemake pipeline and provides interactive tools for biological interpretation and hypothesis generation.
        """)

        st.markdown("""
        **DIT-HAP Pipeline Applications:**
        - Gene essentiality profiling in *S. pombe*
        - Functional genomics research
        - Drug target validation
        - Systems biology studies
        - Transposon insertion sequencing analysis
        """)

    with col2:
        st.info("""
        **🧫 Model System**

        *Schizosaccharomyces pombe* (fission yeast)

        A premier model organism for studying:
        - Fundamental cellular processes
        - Cell cycle regulation
        - Chromosome dynamics
        - Gene essentiality

        Perfect for high-throughput genetic screening approaches.
        """)

    st.markdown("---")

    # Pipeline Integration
    st.header("🔗 DIT-HAP Pipeline Integration")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **Pipeline Data Processing**

        The DIT-HAP pipeline processes raw sequencing data through multiple analysis stages:

        **Insertion-level Analysis:**
        - Base mean expression statistics
        - Log fold change calculations
        - Statistical modeling of fitness effects
        - Quality control and imputation metrics

        **Gene-level Analysis:**
        - Aggregated depletion statistics
        - Model fitting quality assessments
        - Essentiality classifications
        - Statistical confidence intervals
        """)

    with col2:
        st.success("""
        **📊 Data Integration**

        This visualization application directly reads:

        - Standard DIT-HAP output formats
        - Multiple pipeline configurations
        - Automatic file validation
        - Error handling for missing data
        - PomBase reference integration
        """)

    st.markdown("---")

    # Available Analysis Tools
    st.header("📊 Available Visualization & Analysis Tools")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📈 Depletion Curve Plot

        **Pipeline Gene Visualization**

        - Gene depletion curve plotting from pipeline output files
        - Insertion-level statistical analysis and quality control
        - Combined visualizations using Altair charts
        - Interactive gene structure visualization with genomic context
        - Support for multiple pipeline configurations (default, long timecourse, haploid)
        """)

    with col2:
        st.markdown("""
        ### 🎯 Feature Space Analysis

        **Multi-dimensional Pipeline Statistics**

        - Multi-dimensional gene feature visualization from pipeline statistics
        - Interactive scatter plots with gene selection and clustering
        - Comparative analysis across different experimental conditions
        - Pattern identification in pipeline-generated feature matrices
        - Gene filtering and selection based on pipeline metrics
        """)

    with col3:
        st.markdown("""
        ### 🔍 Enrichment Analysis

        **Functional Annotation of Pipeline Results**

        - Gene Ontology (GO) enrichment for pipeline-identified gene sets
        - FYPO (Fission Yeast Phenotype Ontology) analysis for phenotypic interpretations
        - MONDO disease ontology associations for translational insights
        - Statistical significance testing with multiple hypothesis correction
        - Results visualization and export for downstream analysis
        """)

    st.markdown("---")

    # Quick Start Guide
    st.header("🚀 Getting Started with Pipeline Data")

    st.markdown("#### Prerequisites & Setup")

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("""
        **1️⃣ DIT-HAP Pipeline**

        Ensure you have completed the DIT-HAP pipeline:
        - [Install pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)
        - Run complete analysis workflow
        - Generate all required output files
        - Verify pipeline completion status
        """)

    with step2:
        st.markdown("""
        **2️⃣ Data Organization**

        Organize your pipeline outputs:
        - Follow expected directory structure
        - Verify all required files are present
        - Check file naming conventions
        - Validate data integrity
        """)

    with step3:
        st.markdown("""
        **3️⃣ Launch Visualization**

        Start the web application:
        ```bash
        # Clone and setup
        git clone https://github.com/DIT-HAP/DIT_HAP_streamlit.git
        cd DIT_HAP_streamlit
        pip install -r requirements.txt

        # Run application
        streamlit run DIT_HAP_app.py
        ```
        """)

    st.markdown("#### Analysis Workflow")

    workflow1, workflow2, workflow3, workflow4 = st.columns(4)

    with workflow1:
        st.markdown("""
        **🔍 Data Validation**

        - Automatic pipeline output detection
        - File structure verification
        - Configuration validation
        - Reference data checking
        """)

    with workflow2:
        st.markdown("""
        **🧬 Gene Selection**

        - Search by gene name or systematic ID
        - Upload gene lists from pipeline results
        - Filter by essentiality or statistics
        - Query specific gene sets of interest
        """)

    with workflow3:
        st.markdown("""
        **📊 Visualization**

        - Interactive plots with zoom/pan
        - Multiple analysis perspectives
        - Real-time data filtering
        - Comprehensive statistical views
        """)

    with workflow4:
        st.markdown("""
        **💾 Export Results**

        - Download publication-quality figures
        - Export processed data tables
        - Generate analysis reports
        - Prepare for downstream analysis
        """)

    st.markdown("---")

    # Technical Specifications
    st.header("⚙️ Technical Specifications")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🔧 Pipeline Data Requirements**

        **Required Pipeline Output Files:**

        **Insertion-level Analysis:**
        - `annotations.tsv.gz` - Insertion annotations
        - `baseMean.tsv` - Base mean statistics
        - `LFC.tsv` - Log fold change values
        - `fitting_LFCs.tsv` - Statistical modeling
        - `fitting_results.tsv` - Model quality metrics
        - `transformed_weights.tsv` - Statistical weights

        **Gene-level Analysis:**
        - `LFC.tsv` - Aggregated log fold changes
        - `fitting_LFCs.tsv` - Gene-level statistical modeling
        - `fitting_results.tsv` - Model quality assessments

        **Reference Data:**
        - PomBase gene annotations
        - Genome intervals and features
        - Ontology files (GO, FYPO, MONDO)
        """)

        st.markdown("""
        **🗂️ Data Organization**

        ```
        data/
        ├── raw/                           # DIT-HAP pipeline outputs
        │   ├── HD_DIT_HAP/               # Standard pipeline results
        │   ├── Long_timecourse_data/     # Extended timecourse
        │   └── haploid_data/             # Haploid-specific analysis
        └── resource/                     # Reference data
            └── pombase_data/            # PomBase annotations
        ```
        """)

    with col2:
        st.markdown("""
        **💻 Application Architecture**

        **Core Framework:**
        - **Streamlit** (≥1.51.0) - Web application framework
        - **Pandas** (≥2.3.0) - Data manipulation and analysis
        - **NumPy** (≥2.3.0) - Numerical computing foundation
        - **Pydantic** (≥2.11.7) - Data validation and configuration

        **Visualization Stack:**
        - **Altair** (≥5.5.0) - Interactive statistical visualizations
        - **Matplotlib** (≥3.10.0) - Static plotting capabilities

        **Bioinformatics Tools:**
        - **goatools** (≥1.5.2) - Gene Ontology enrichment analysis
        - **BeautifulSoup4** + **lxml** - XML/HTML parsing
        - **NetworkX** - Network analysis and graph algorithms

        **Network Analysis:**
        - **NDEx2** - Network data exchange integration
        - **st-cytoscape** - Interactive network visualization
        - **GO-CAM** - Causal activity model support
        """)

    st.markdown("---")

    # Supported Pipeline Configurations
    st.header("🔬 Supported Pipeline Configurations")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🧬 Standard Pipeline**

        `HD_DIT_HAP/` dataset

        - Complete diploid analysis
        - Multiple time course experiments
        - Biological replicates
        - Standard statistical models
        - Comprehensive quality metrics
        """)

    with col2:
        st.markdown("""
        **⏰ Extended Timecourse**

        `Long_timecourse_data/` dataset

        - Extended experimental duration
        - Additional sampling points
        - Enhanced temporal resolution
        - Long-term fitness tracking
        """)

    with col3:
        st.markdown("""
        **🔬 Haploid Analysis**

        `haploid_data/` dataset

        - Haploid-specific workflows
        - Essentiality profiling
        - Phenotype characterization
        - Single-chromosome analysis
        """)

    st.markdown("---")

    # Resources and Support
    st.header("📚 Resources & Support")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📖 Documentation**

        - [Pipeline Documentation](https://github.com/DIT-HAP/DIT_HAP_pipeline) - Complete workflow guide
        - [PomBase](https://www.pombase.org/) - Gene database for *S. pombe*
        - [GO Consortium](http://geneontology.org/) - Gene Ontology terms
        - Methodology and API documentation
        """)

    with col2:
        st.markdown("""
        **🔗 External Resources**

        - [DIT-HAP Pipeline Repository](https://github.com/DIT-HAP/DIT_HAP_pipeline)
        - [FYPO Ontology](https://github.com/pombase/fypo) - Fission yeast phenotypes
        - [MONDO Disease Ontology](https://github.com/mondo-initiative/mondo)
        - [Streamlit Documentation](https://docs.streamlit.io/)
        """)

    with col3:
        st.markdown("""
        **🧪 Pipeline Support**

        **For pipeline-specific questions:**
        - [Pipeline Issues](https://github.com/DIT-HAP/DIT_HAP_pipeline/issues)
        - Installation and setup guidance
        - Analysis methodology support
        - Computational requirements
        """)

    st.markdown("---")

    # Citation
    st.header("📄 Citation Information")

    st.markdown("""
    If you use the DIT-HAP pipeline and this visualization tool in your research, please cite both:

    **DIT-HAP Pipeline:**
    > DIT-HAP: Diploid Insertional Mutagenesis by Transposon and Haploid Analysis of Phenotype - A comprehensive pipeline for transposon mutagenesis analysis in *Schizosaccharomyces pombe*

    **DIT-HAP Streamlit Visualization:**
    > DIT-HAP Streamlit Visualization - Interactive web application for exploring and analyzing DIT-HAP pipeline results
    """)

    # Footer
    st.markdown("---")

    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem; padding: 1rem; border-top: 1px solid #ddd;'>
        <strong>DIT-HAP Streamlit Visualization</strong> •
        Interactive Analysis Component for <a href='https://github.com/DIT-HAP/DIT_HAP_pipeline' target='_blank'>DIT-HAP Pipeline</a> •
        Powered by <a href='https://www.pombase.org/' target='_blank'>PomBase</a> •
        Version 1.0
    </div>
    """, unsafe_allow_html=True)

# Run the main page content
show_main_page()