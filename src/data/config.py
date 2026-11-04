"""
Dataset Path Configuration
==========================

Config-driven path resolution for the DIT-HAP Streamlit application. Reads
config/datasets.yaml (the dataset registry) and builds typed, immutable path
containers for each dataset. Replaces the former hardcoded get_default_config /
get_long_timecourse_config / get_haploid_config trio.

The fixed sub-paths below (insertion_level/LFC.tsv, gene_level/fitting_results.tsv,
...) are the contract shared with the upstream `release/` packaging rule.

Input
-----
- config/datasets.yaml: dataset registry (data_dir, has_imputation, reference).

Output
------
- DataConfig instances (frozen dataclasses) consumed by src/data/loader.py.

Author:   Yusheng Yang (guidance) + Claude (implementation)
Date:     2026-07-14
Version:  1.0.0
"""

# =============================================================================
# IMPORTS
# =============================================================================
# 1. Standard Library Imports
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

# 3. Third-party Imports
import yaml

# =============================================================================
# GLOBAL CONSTANTS
# =============================================================================
DATASETS_YAML = Path("config/datasets.yaml")

# Per-dataset files, relative to a dataset's data_dir (upstream release contract).
INSERTION_LEVEL_FILES = {
    "insertion_annotations": "insertion_level/annotations.tsv.gz",
    "insertion_level_baseMean": "insertion_level/baseMean.tsv",
    "insertion_level_LFCs": "insertion_level/LFC.tsv",
    "insertion_level_weights": "insertion_level/insertion_weights.tsv",
    "insertion_level_fitting_LFCs": "insertion_level/fitting_LFCs.tsv",
    "insertion_level_fitting_results": "insertion_level/fitting_results.tsv",
}
IMPUTATION_STATISTICS_FILE = "insertion_level/imputation_statistics.tsv"
GENE_LEVEL_FILES = {
    "gene_level_LFCs": "gene_level/LFC.tsv",
    "gene_level_fitting_LFCs": "gene_level/fitting_LFCs.tsv",
    "gene_level_fitting_results": "gene_level/fitting_results.tsv",
}

# Reference sub-paths, relative to the versioned pombase_data directory (shared).
GENE_METADATA_FILES = {
    "gene_IDs_names_products": "Gene_metadata/gene_IDs_names_products.tsv",
    "genome_intervals": "genome_region/genome_intervals.bed",
}
GENE_ONTOLOGY_FILES = {
    "gene_ontology_obo": "ontologies_and_associations/go-basic.obo",
    "gene_ontology_association_gaf": "ontologies_and_associations/gene_ontology_annotation.gaf.tsv",
}
GOSLIM_TERMS_FILES = [
    "ontologies_and_associations/bp_go_slim_terms.tsv",
    "ontologies_and_associations/cc_go_slim_terms.tsv",
    "ontologies_and_associations/mf_go_slim_terms.tsv",
]
FYPO_FILES = {
    "fypo_obo": "ontologies_and_associations/fypo-simple-pombase.obo",
    "fypo_gaf": "ontologies_and_associations/pombase_phenotype_annotation.phaf.tsv",
    "fypo_slim": "ontologies_and_associations/fypo_slim_ids_and_names.tsv",
}
MONDO_FILES = {
    "mondo_obo": "ontologies_and_associations/mondo-simple.obo",
    "mondo_gaf": "ontologies_and_associations/human_disease_association.tsv",
    "mondo_slim": "ontologies_and_associations/pombe_mondo_disease_slim_terms.tsv",
}


# =============================================================================
# CONFIGURATION DATACLASSES
# =============================================================================
# frozen=True for immutability + safe reuse; slots omitted so Streamlit's
# @st.cache_data hashing can introspect these when used as cache keys.

@dataclass(kw_only=True, frozen=True)
class GeneMetadataConfig:
    """Paths for gene metadata (shared reference data)."""

    gene_IDs_names_products: Path
    deletion_library_essentiality: Path
    genome_intervals: Path

    def validate_paths(self) -> None:
        """Raise if any metadata file is missing or not a regular file."""
        for file_path in self.__dict__.values():
            if not file_path.exists():
                raise FileNotFoundError(f"Gene metadata file not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")


@dataclass(kw_only=True, frozen=True)
class InsertionLevelConfig:
    """Paths for insertion-level statistics (per-dataset)."""

    insertion_annotations: Path
    insertion_level_baseMean: Path
    insertion_level_LFCs: Path
    insertion_level_weights: Path
    insertion_level_fitting_LFCs: Path
    insertion_level_fitting_results: Path
    imputation_statistics: Path | None = None

    def validate_paths(self) -> None:
        """Raise if any required insertion-level file is missing."""
        required = [
            self.insertion_annotations, self.insertion_level_baseMean,
            self.insertion_level_LFCs, self.insertion_level_weights,
            self.insertion_level_fitting_LFCs, self.insertion_level_fitting_results,
        ]
        for file_path in required:
            if not file_path.exists():
                raise FileNotFoundError(f"Insertion level file not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
        if self.imputation_statistics and not self.imputation_statistics.exists():
            raise FileNotFoundError(
                f"Imputation statistics file not found: {self.imputation_statistics}"
            )


@dataclass(kw_only=True, frozen=True)
class GeneLevelConfig:
    """Paths for gene-level statistics (per-dataset)."""

    gene_level_LFCs: Path
    gene_level_fitting_LFCs: Path
    gene_level_fitting_results: Path

    def validate_paths(self) -> None:
        """Raise if any gene-level file is missing or not a regular file."""
        for file_path in self.__dict__.values():
            if not file_path.exists():
                raise FileNotFoundError(f"Gene level file not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")


@dataclass(kw_only=True, frozen=True)
class GeneOntologyDataConfig:
    """Paths for Gene Ontology data (shared reference data)."""

    gene_ontology_obo: Path
    gene_ontology_association_gaf: Path
    goslim_terms_table: list[Path] = field(default_factory=list)

    def validate_paths(self) -> None:
        """Raise if any GO file is missing or not a regular file."""
        for file_path in [self.gene_ontology_obo, self.gene_ontology_association_gaf, *self.goslim_terms_table]:
            if not file_path.exists():
                raise FileNotFoundError(f"Gene ontology file not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")


@dataclass(kw_only=True, frozen=True)
class FYPODataConfig:
    """Paths for fission yeast phenotype ontology data (shared reference data)."""

    fypo_obo: Path
    fypo_gaf: Path
    fypo_slim_ids_and_names_table: list[Path] = field(default_factory=list)

    def validate_paths(self) -> None:
        """Raise if any FYPO file is missing or not a regular file."""
        for file_path in [self.fypo_obo, self.fypo_gaf, *self.fypo_slim_ids_and_names_table]:
            if not file_path.exists():
                raise FileNotFoundError(f"FYPO data file not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")


@dataclass(kw_only=True, frozen=True)
class MONDODataConfig:
    """Paths for Mondo Disease Ontology data (shared reference data)."""

    mondo_obo: Path
    mondo_gaf: Path
    mondo_slim_ids_and_names_table: list[Path] = field(default_factory=list)

    def validate_paths(self) -> None:
        """Raise if any MONDO file is missing or not a regular file."""
        for file_path in [self.mondo_obo, self.mondo_gaf, *self.mondo_slim_ids_and_names_table]:
            if not file_path.exists():
                raise FileNotFoundError(f"MONDO data file not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")


@dataclass(kw_only=True, frozen=True)
class DataConfig:
    """Aggregate of all path configs for a single dataset."""

    gene_metadata: GeneMetadataConfig
    insertion_level: InsertionLevelConfig
    gene_level: GeneLevelConfig
    gene_ontology_data: GeneOntologyDataConfig
    gene_phenotype_data: FYPODataConfig
    mondo_disease_ontology_data: MONDODataConfig

    def validate_all_paths(self) -> None:
        """Validate every path across all sub-configs."""
        self.gene_metadata.validate_paths()
        self.insertion_level.validate_paths()
        self.gene_level.validate_paths()
        self.gene_ontology_data.validate_paths()
        self.gene_phenotype_data.validate_paths()
        self.mondo_disease_ontology_data.validate_paths()


# =============================================================================
# CORE LOGIC
# =============================================================================

@cache
def _load_registry() -> dict:
    """Read and cache the dataset registry from config/datasets.yaml."""
    with DATASETS_YAML.open() as f:
        return yaml.safe_load(f)


def list_datasets() -> dict[str, str]:
    """Return {dataset_name: label} for all registered datasets."""
    registry = _load_registry()
    return {name: entry["label"] for name, entry in registry["datasets"].items()}


def default_dataset_name() -> str:
    """Return the dataset selected by default on first load."""
    registry = _load_registry()
    return registry.get("default_dataset", next(iter(registry["datasets"])))


def _build_reference_configs(
    pombase_dir: Path, resource_dir: Path
) -> tuple[GeneMetadataConfig, GeneOntologyDataConfig, FYPODataConfig, MONDODataConfig]:
    """Build the four shared reference configs from the versioned pombase dir."""
    essentiality = resource_dir / "Hayles_2013_OB_merged_categories_sysIDupdated.xlsx"
    gene_metadata = GeneMetadataConfig(
        gene_IDs_names_products=pombase_dir / GENE_METADATA_FILES["gene_IDs_names_products"],
        deletion_library_essentiality=essentiality,
        genome_intervals=pombase_dir / GENE_METADATA_FILES["genome_intervals"],
    )
    gene_ontology = GeneOntologyDataConfig(
        gene_ontology_obo=pombase_dir / GENE_ONTOLOGY_FILES["gene_ontology_obo"],
        gene_ontology_association_gaf=pombase_dir / GENE_ONTOLOGY_FILES["gene_ontology_association_gaf"],
        goslim_terms_table=[pombase_dir / p for p in GOSLIM_TERMS_FILES],
    )
    fypo = FYPODataConfig(
        fypo_obo=pombase_dir / FYPO_FILES["fypo_obo"],
        fypo_gaf=pombase_dir / FYPO_FILES["fypo_gaf"],
        fypo_slim_ids_and_names_table=[pombase_dir / FYPO_FILES["fypo_slim"]],
    )
    mondo = MONDODataConfig(
        mondo_obo=pombase_dir / MONDO_FILES["mondo_obo"],
        mondo_gaf=pombase_dir / MONDO_FILES["mondo_gaf"],
        mondo_slim_ids_and_names_table=[pombase_dir / MONDO_FILES["mondo_slim"]],
    )
    return gene_metadata, gene_ontology, fypo, mondo


def load_dataset_config(name: str | None = None) -> DataConfig:
    """Build a DataConfig for a registered dataset (default if name is None)."""
    registry = _load_registry()
    if name is None:
        name = default_dataset_name()
    if name not in registry["datasets"]:
        raise KeyError(f"Unknown dataset {name!r}; registered: {list(registry['datasets'])}")

    entry = registry["datasets"][name]
    data_dir = Path(entry["data_dir"])
    ref = registry["reference"]
    pombase_dir = Path(ref["pombase_dir"]) / ref["pombase_version"]
    resource_dir = Path(ref["resource_dir"])

    gene_metadata, gene_ontology, fypo, mondo = _build_reference_configs(pombase_dir, resource_dir)
    insertion_level = InsertionLevelConfig(
        **{key: data_dir / rel for key, rel in INSERTION_LEVEL_FILES.items()},
        imputation_statistics=(data_dir / IMPUTATION_STATISTICS_FILE) if entry.get("has_imputation") else None,
    )
    gene_level = GeneLevelConfig(**{key: data_dir / rel for key, rel in GENE_LEVEL_FILES.items()})

    return DataConfig(
        gene_metadata=gene_metadata,
        insertion_level=insertion_level,
        gene_level=gene_level,
        gene_ontology_data=gene_ontology,
        gene_phenotype_data=fypo,
        mondo_disease_ontology_data=mondo,
    )


def get_default_config() -> DataConfig:
    """Backward-compatible: config for the registry's default dataset."""
    return load_dataset_config(None)


def get_long_timecourse_config() -> DataConfig:
    """Backward-compatible: config for the long-timecourse dataset."""
    return load_dataset_config("Long_timecourse")


def get_haploid_config() -> DataConfig:
    """Backward-compatible: config for the haploid dataset."""
    return load_dataset_config("Haploid")
