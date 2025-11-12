import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="DIT-HAP Analysis Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="auto"
)

# Define pages
plot_page = st.Page("pages/depletion_data.py", title="Curve plot", icon=":material/timeline:")
feature_space_page = st.Page("pages/feature_space.py", title="Feature space", icon=":material/scatter_plot:")
enrichment_page = st.Page("pages/enrichment_analysis.py", title="Enrichment analysis", icon=":material/search_insights:")

# Create navigation
pg = st.navigation(
        {
            "Visualization": [plot_page, feature_space_page],
            "Analysis": [enrichment_page],
        }
    )

# Main page content
def show_main_page():
    # Application Header
    st.title("🧬 DIT-HAP Analysis Tool")
    st.markdown("### Diploid for Insertional Mutagenesis by Transposon and Haploid for Analysis of Phenotype")
    st.markdown("_A comprehensive web application for analyzing transposon insertion sequencing data and gene essentiality in *Schizosaccharomyces pombe*_")

    st.markdown("---")

    # About Section
    st.header("🔬 About DIT-HAP")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        **DIT-HAP** is a powerful genetic screening methodology that combines:

        - **Diploid insertional mutagenesis**: Random transposon insertions in diploid cells
        - **Haploid analysis**: Selection and analysis of haploid derivatives

        This approach enables systematic identification of essential genes by measuring how gene disruptions affect cellular fitness over time.
        """)

        st.markdown("""
        **Applications:**
        - Gene essentiality profiling
        - Drug target validation
        - Functional genomics research
        - Systems biology studies
        """)

    with col2:
        st.info("""
        **🧫 Model Organism**

        *Schizosaccharomyces pombe* (fission yeast)

        A well-established model for studying fundamental cellular processes, cell cycle regulation, and chromosome dynamics.
        """)

    st.markdown("---")

    # Features Overview
    st.header("📊 Available Analysis Tools")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📈 Curve Plot

        **Gene Depletion Visualization**

        - Interactive depletion curve plotting
        - Time-series analysis of gene fitness
        - Individual gene interrogation
        - Statistical confidence intervals
        - Multiple time course support
        """)

    with col2:
        st.markdown("""
        ### 🎯 Feature Space

        **Multi-dimensional Analysis**

        - 2D and 3D feature space visualization
        - Gene clustering and patterns
        - Interactive scatter plots
        - Comparative analysis tools
        - Custom parameter selection
        """)

    with col3:
        st.markdown("""
        ### 🔍 Enrichment Analysis

        **Functional Annotation**

        - Gene Ontology (GO) enrichment
        - FYPO phenotype enrichment
        - MONDO disease ontology
        - Statistical significance testing
        - Pathway analysis
        """)

    st.markdown("---")

    # Quick Start Guide
    st.header("🚀 Quick Start Guide")

    st.markdown("#### Getting Started with Your Analysis")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("""
        **1️⃣ Select Genes**

        Enter gene names or upload a gene list
        - Individual genes: `cdc2`, `wee1`
        - Multiple genes: `cdc2, wee1, rum1`
        - File upload: CSV/TSV format
        """)

    with step2:
        st.markdown("""
        **2️⃣ Choose Analysis**

        Navigate to your desired tool:
        - **Curve Plot**: For depletion analysis
        - **Feature Space**: For comparative visualization
        - **Enrichment**: For functional insights
        """)

    with step3:
        st.markdown("""
        **3️⃣ Analyze Results**

        Explore interactive visualizations:
        - Zoom and pan on plots
        - Hover for detailed information
        - Filter and select data points
        - Export high-quality figures
        """)

    with step4:
        st.markdown("""
        **4️⃣ Export Findings**

        Save your analysis results:
        - Download plots as PNG/SVG
        - Export data tables
        - Generate analysis reports
        - Cite properly in publications
        """)

    st.markdown("---")

    # Data Information
    st.header("📚 Data Sources & Versions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🧬 Reference Data**

        - **Primary Source**: [PomBase](https://www.pombase.org/)
        - **Gene Annotations**: Latest PomBase release
        - **Genome Assembly**: *S. pombe* reference genome
        - **Ontology Terms**: GO, FYPO, and MONDO

        **🔬 Experimental Data**

        - **Method**: Transposon insertion sequencing
        - **Organism**: *S. pombe* (fission yeast)
        - **Time Courses**: Multiple experimental conditions
        - **Replicates**: Biological replicates included
        """)

    with col2:
        st.markdown("""
        **📖 Citation Information**

        If you use this tool in your research, please cite:

        > DIT-HAP: A comprehensive approach for gene essentiality profiling in *Schizosaccharomyces pombe*

        **🔧 Technical Details**

        - **Framework**: Streamlit web application
        - **Data Processing**: Pydantic validation
        - **Visualization**: Altair interactive charts
        - **Analysis**: Statistical enrichment methods
        - **Compatibility**: Modern web browsers
        """)

    st.markdown("---")

    # Navigation Guide
    st.header("🧭 How to Use Each Page")

    st.markdown("""
    **📊 Visualization Pages**

    - **Curve Plot**: Start here for individual gene analysis. Ideal for detailed examination of gene depletion kinetics and fitness effects over time.
    - **Feature Space**: Use for comparative analysis. Perfect for identifying gene clusters and patterns in multi-dimensional parameter space.

    **🔍 Analysis Pages**

    - **Enrichment Analysis**: Apply after identifying gene sets. Provides functional insights through statistical enrichment testing of biological annotations.
    """)

    st.markdown("---")

    # Footer
    st.markdown("---")

    # Contact and Support section
    st.markdown("### 💡 Need Help?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📖 Documentation**

        - User guides and tutorials
        - API documentation
        - Methodology details
        """)

    with col2:
        st.markdown("""
        **🔗 Resources**

        - [PomBase](https://www.pombase.org/) - Gene database
        - [GO Consortium](http://geneontology.org/) - Gene Ontology
        - [FYPO Ontology](https://github.com/pombase/fypo) - Phenotype terms
        """)

    with col3:
        st.markdown("""
        **📧 Support**

        - Technical assistance
        - Data format questions
        - Analysis guidance
        """)

    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem; padding: 1rem; border-top: 1px solid #ddd;'>
        <strong>DIT-HAP Analysis Tool</strong> •
        Advanced genetic screening analysis platform •
        <a href='https://www.pombase.org/' target='_blank'>PomBase</a> integration •
        Version 1.0
    </div>
    """, unsafe_allow_html=True)

# Show main page content
show_main_page()

# Run navigation
pg.run()


