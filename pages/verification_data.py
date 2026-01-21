# ================================= Imports =================================
import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# ================================= Constants =================================
VERIFICATION_DATA_DIR_URL = "https://github.com/DIT-HAP/DIT_HAP_streamlit/blob/main/data/tetrad_plate_images"

# ================================= Functions =================================
def image_to_base64(image_path):
    """Local image file to base64 string conversion."""
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    suffix = Path(image_path).suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp"
    }
    mime = mime_types.get(suffix, "image/png")
    return f"data:{mime};base64,{data}"

@st.dialog("❓ How to Use This Tool", width="large")
def how_to_use_this_tool():
    """Dialog explaining how to use the verification data tool."""
    st.markdown("""
        **Step 1: Browse the Data Table**
        - Scroll through the verification data table to view all entries
        - Use the search/filter functionality to find specific genes
        - Sort columns by clicking on column headers
        - Resize columns as needed for better viewing

        **Step 2: View Plate Images**
        - **3d-6d images**: Cropped tetrad images showing colony growth over 3-6 days
        - **Color YES/HYG/NAT/LEU/ADE images**: Color plates showing auxotrophic markers
        - Click on images to view them at full resolution
        - Compare growth patterns across different time points

        **Step 3: Analyze Phenotypes**
        - Assess colony size and growth rate from time series images
        - Check color plates for auxotrophic marker validation
        - Compare phenotypes across different genetic backgrounds
        - Cross-reference with depletion analysis results

        **Step 4: Export Data**
        - Use the download button to export the full table
        - Save images for publication or presentation
        - Combine data with other analysis results
        """)

@st.dialog("🔬 Understanding Verification Data", width="large")
def understanding_verification_data():
    """Dialog explaining the verification data."""
    st.markdown("""
        **What is Verification Data?**

        Verification data provides experimental validation of DIT-HAP pipeline results:
        - **Tetrad analysis**: Traditional yeast genetic technique for studying gene segregation
        - **Phenotype validation**: Confirms predicted essentiality from depletion analysis
        - **Auxotrophic markers**: Color plates verify nutritional requirements
        - **Time course**: Documents colony growth over multiple days

        **Data Columns:**
        - **Gene information**: Systematic ID, gene name, deletion status
        - **Round**: Experimental round number
        - **Image paths**: Links to cropped plate images at different time points
        - **Phenotype annotations**: Manual curation of observed phenotypes

        **Plate Types:**
        - **3d-6d images**: Growth progression over time (day 3-6)
        - **YES**: Yellow minimal media with supplements
        - **HYG**: Hygromycin resistance marker
        - **NAT**: Nourseothricin resistance marker
        - **LEU**: Leucine auxotrophy marker
        - **ADE**: Adenine auxotrophy marker
        """)

@st.dialog("⚙️ Data Requirements", width="large")
def data_requirements():
    """Dialog explaining the data requirements for verification data."""
    st.markdown("""
        **Required Data Files:**
        - **Excel summary file**: Combined verification data with manual annotations
        - **Plate images**: Cropped tetrad images for each time point and condition
        - **Color plate images**: Auxotrophic marker validation plates

        **Data Organization:**
        - Images stored in `data/tetrad_plate_images/` directory
        - Excel file contains image path references and phenotype annotations
        - Images are encoded as base64 for web display
        - File naming convention follows round and gene identification

        **Image Format:**
        - Standard image formats (PNG, JPG) supported
        - Automatic conversion to base64 for embedding
        - Optimal sizing for web viewing
        - High-resolution images for detailed examination
        """)

@st.dialog("🎯 Analysis Tips", width="large")
def analysis_tips():
    """Dialog providing analysis tips for interpreting verification data."""
    st.markdown("""
        **Interpreting Growth Patterns:**
        - **Essential genes**: No colony growth or very small colonies
        - **Non-essential genes**: Normal colony size and growth rate
        - **Slow-growing genes**: Reduced colony size compared to wild-type
        - **Conditional genes**: Growth defects only under specific conditions

        **Color Plate Interpretation:**
        - **YES plate**: General growth control
        - **Antibiotic plates**: Verify resistance marker integration
        - **Auxotrophic plates**: Confirm nutritional requirements
        - **Color intensity**: Indicates strength of auxotrophic phenotype

        **Integration with DIT-HAP Results:**
        - **Depletion curves**: Genes showing strong depletion should show growth defects
        - **Gene essentiality**: Verify pipeline predictions with experimental data
        - **False positives**: Check if pipeline over-predicted essentiality
        - **False negatives**: Identify essential genes missed by pipeline

        **Quality Control:**
        - **Plate contamination**: Look for non-colony growth patterns
        - **Edge effects**: Colonies at plate edges may grow differently
        - **Replicate consistency**: Compare results across experimental replicates
        - **Manual curation**: Refer to phenotype annotations for expert interpretation
        """)

def main():
    """Main entry point for the Verification Data page."""

    st.title("🧬 Verification Data for DIT-HAP")

    # Introduction and Usage Guide
    st.markdown("""
    ### 🔬 Experimental Validation of DIT-HAP Pipeline Results

    This page provides **verification data** from tetrad analysis experiments that validate the findings of the **[DIT-HAP pipeline](https://github.com/DIT-HAP/DIT_HAP_pipeline)**.
    Browse plate images and phenotype annotations to confirm gene essentiality predictions.
    """)

    usage_guides = {
        "❓ How to Use This Tool": how_to_use_this_tool,
        "🔬 Understanding Verification Data": understanding_verification_data,
        "⚙️ Data Requirements": data_requirements,
        "🎯 Analysis Tips": analysis_tips
    }
    st.segmented_control(
        label="📖 Usage Guides",
        options=list(usage_guides.keys()),
        key="usage_guide_selector",
        on_change=lambda: usage_guides[st.session_state.usage_guide_selector](),
        width="stretch",
        label_visibility="collapsed"
    )
    
    df = pd.read_excel(
        "./data/resource/all_rounds_combined_verification_summary_manually_annotated.xlsx"
    )

    df_18round = df.query("round == '18th_round'").copy()

    # Replace local disk paths with GitHub URLs
    path_mapping = {
        "/hugedata/YushengYang/DIT_HAP_verification/data/cropped_images/DIT_HAP_deletion/18th_round/3d": "data/tetrad_plate_images",
        "/hugedata/YushengYang/DIT_HAP_verification/data/cropped_images/DIT_HAP_deletion/18th_round/4d": "data/tetrad_plate_images",
        "/hugedata/YushengYang/DIT_HAP_verification/data/cropped_images/DIT_HAP_deletion/18th_round/5d": "data/tetrad_plate_images",
        "/hugedata/YushengYang/DIT_HAP_verification/data/cropped_images/DIT_HAP_deletion/18th_round/6d": "data/tetrad_plate_images",
        "/hugedata/YushengYang/DIT_HAP_verification/data/cropped_images/DIT_HAP_deletion/18th_round/replica": "data/tetrad_plate_images",
    }
    df_18round.replace(path_mapping, regex=True, inplace=True)
    df_18round["3d_image_path"] = df_18round["3d_image_path"].apply(image_to_base64)
    df_18round["4d_image_path"] = df_18round["4d_image_path"].apply(image_to_base64)
    df_18round["5d_image_path"] = df_18round["5d_image_path"].apply(image_to_base64)
    df_18round["6d_image_path"] = df_18round["6d_image_path"].apply(image_to_base64)
    df_18round["YES_image_path"] = df_18round["YES_image_path"].apply(image_to_base64)
    df_18round["HYG_image_path"] = df_18round["HYG_image_path"].apply(image_to_base64)
    df_18round["NAT_image_path"] = df_18round["NAT_image_path"].apply(image_to_base64)
    df_18round["LEU_image_path"] = df_18round["LEU_image_path"].apply(image_to_base64)
    df_18round["ADE_image_path"] = df_18round["ADE_image_path"].apply(image_to_base64)
    # df_18round.replace("_#", "_%", regex=True, inplace=True)
    st.data_editor(
        df_18round,
        column_config={
            "3d_image_path": st.column_config.ImageColumn(
                "3d  image", help="Cropped image at 3 days.",
            ),
            "4d_image_path": st.column_config.ImageColumn(
                "4d  image", help="Cropped image at 4 days.",
            ),
            "5d_image_path": st.column_config.ImageColumn(
                "5d  image", help="Cropped image at 5 days.",
            ),
            "6d_image_path": st.column_config.ImageColumn(
                "6d  image", help="Cropped image at 6 days.",
            ),
            "YES_image_path": st.column_config.ImageColumn(
                "Color YES image", help="Cropped image of color YES plate.",
            ),
            "HYG_image_path": st.column_config.ImageColumn(
                "HYG image", help="Cropped image of color HYG plate.",
            ),
            "NAT_image_path": st.column_config.ImageColumn(
                "NAT image", help="Cropped image of color NAT plate.",
            ),
            "LEU_image_path": st.column_config.ImageColumn(
                "LEU image", help="Cropped image of color LEU plate.",
            ),
            "ADE_image_path": st.column_config.ImageColumn(
                "ADE image", help="Cropped image of color ADE plate.",
            ),
        },
        hide_index=True,
        key="verification_data_editor",
    )

if __name__ == "__main__":
    main()