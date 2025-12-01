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

def main():
    """Main entry point for the Verification Data page."""
    
    st.title("🧬 Verification Data for DIT-HAP")
    # st.info(
    #     """
    #     This page provides access to verification data used in the DIT-HAP project.
    #     You can explore various datasets and images that validate the findings of our research.

    #     The verification data is hosted on GitHub and can be accessed directly via the link below.
    #     """
    # )
    
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