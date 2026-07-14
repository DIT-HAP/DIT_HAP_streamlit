#!/bin/bash
# =============================================================================
# yaml2cx2.sh — convert PomBase GO-CAM YAML models to CX2 for the app.
#
# Downstream-owned data-prep step (NOT part of the upstream Snakemake pipeline).
# Reads data/resource/pombe_gocam/*.yaml and writes data/resource/pombe_gocam_cx2/.
#
# Run from the repository root:
#     bash scripts/yaml2cx2.sh
# =============================================================================
set -euo pipefail

# Resolve repo root as the parent of this script's directory, so the script
# works regardless of the current working directory.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${REPO_ROOT}/data/resource/pombe_gocam"
OUT_DIR="${REPO_ROOT}/data/resource/pombe_gocam_cx2"

mkdir -p "${OUT_DIR}"
find "${SRC_DIR}" -name "*.yaml" | while read -r file; do
    gocam convert --dot-layout -I yaml -O cx2 "${file}" \
        -o "${OUT_DIR}/$(basename "${file}" .yaml).cx2"
done
