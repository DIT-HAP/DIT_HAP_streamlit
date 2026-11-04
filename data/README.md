# Data provenance

This directory holds all data consumed by the DIT-HAP Streamlit app. Sources
fall into three groups: **upstream project results**, **upstream reference
data**, and **downstream-owned resources**. The dataset registry
(`config/datasets.yaml`) maps logical dataset names to these paths.

## `raw/{dataset}/` — upstream project results

Copied from the upstream `DIT_HAP_snakemake` pipeline's per-project `release/`
folder (produced by the `package_release` rule). One subfolder per dataset:

| Folder | Upstream project |
|---|---|
| `raw/HD_DIT_HAP/` | `projects/HD_DIT_HAP/release/` |
| `raw/Long_timecourse_data/` | `projects/Spore2YES6_1328/release/` |
| `raw/haploid_data/` | `projects/LD_haploid/release/` |

Each holds `insertion_level/` and `gene_level/` with the fixed filenames that
form the upstream↔downstream contract (see `src/data/config.py`):
`LFC.tsv`, `fitting_LFCs.tsv`, `fitting_results.tsv`, plus the auxiliary files
`annotations.tsv.gz`, `baseMean.tsv`, `insertion_weights.tsv`, and
(datasets with replicates only) `imputation_statistics.tsv`.

**Sign convention:** upstream reports depletion as **negative** LFC and
**negative** fitted parameters A/DR (since `29f1aba`, 2026-09-09; release
regenerated 2026-09-17); more negative means stronger or faster depletion.
`insertion_weights.tsv` is long-format (one row per insertion × timepoint ×
gene).

`gene_level/all_coding_genes_with_DIT_HAP_clustering.tsv` is downstream-generated:
it joins the HD release's fitting results with the selected clustering variant
from `DIT_HAP_analysis`
(`results/clustering/HD_DIT_HAP/kmeans_direct9/final_clusters.tsv`).

**To refresh:** `cp -r <upstream>/projects/{project}/release/* data/raw/{dataset}/`.

## `resource/pombase_data/{version}/` — upstream reference data

Versioned PomBase reference data, shared across all datasets. Packaged upstream
by the `package_reference` rule; copy the needed version directory here. The
active version is set by `reference.pombase_version` in `config/datasets.yaml`.

## Downstream-owned resources (not from the upstream pipeline)

Maintained within this repository. Their provenance:

| Path | Source / how to regenerate |
|---|---|
| `resource/pombe_gocam/` | PomBase GO-CAM YAML models (downloaded) |
| `resource/pombe_gocam_cx2/` | Generated from the YAML via `scripts/yaml2cx2.sh` |
| `resource/pombe_gocam_json/` | GO-CAM JSON exports (downloaded) |
| `resource/kegg_pathways/` | KEGG pathway exports (downloaded) |
| `resource/Hayles_2013_OB_merged_categories_sysIDupdated.xlsx` | Hayles et al. 2013 deletion-library categories, systematic IDs updated |
| `resource/collected_pombe_gene_features.csv` | Collected S. pombe gene features |
| `resource/all_rounds_combined_verification_summary_manually_annotated.xlsx` | Manually annotated verification summary |
