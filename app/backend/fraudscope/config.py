"""Paths and constants shared by the export scripts and the API."""

import os
from pathlib import Path

# app/backend/fraudscope/config.py -> repo root is three parents up from this file's folder
REPO_ROOT: Path = Path(__file__).resolve().parents[3]
DATA_DIR: Path = REPO_ROOT / "data"
ARTIFACT_DIR: Path = REPO_ROOT / "app" / "backend" / "artifacts"
# The results CSVs shipped with the backend (copied by export/copy_results.py in Task 5).
RESULTS_DIR: Path = ARTIFACT_DIR / "results"
# The research results folder (source for the copy and for the reproduction gate).
SOURCE_RESULTS_DIR: Path = REPO_ROOT / "results"

FEATURES: list[str] = ["V10", "V12", "V14", "V17"]
RANDOM_STATE: int = 42

# Random Forest operating threshold (default, not tuned on test labels).
RF_THRESHOLD: float = 0.5

# Upload limits.
RF_MAX_ROWS: int = 50_000
MAX_UPLOAD_BYTES: int = 5_000_000

# Quantum caps (measured locally: QSVM 25 rows ~9s, VQC 200 rows ~0.7s) and live timeout.
QSVM_MAX_ROWS: int = 25
VQC_MAX_ROWS: int = 200
LIVE_TIMEOUT_S: float = float(os.environ.get("LIVE_TIMEOUT_S", "20"))
