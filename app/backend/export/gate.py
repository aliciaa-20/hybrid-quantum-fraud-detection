"""Reproduction gate: checks that retrained models match the paper's saved results.

Any failure raises GateFailure; export scripts must not save artifacts after one.
"""

import json
import subprocess
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from fraudscope import config


class GateFailure(Exception):
    pass


def read_results_csv(path) -> pd.DataFrame:
    # keep_default_na=False: the balancing label "None" is a string, not a missing value.
    return pd.read_csv(path, keep_default_na=False)


def load_test() -> pd.DataFrame:
    return pd.read_csv(config.DATA_DIR / "test_selected.csv")


def check_alignment(test: pd.DataFrame, predictions: pd.DataFrame, balancing: str) -> None:
    """Rows of `predictions` for this balancing must line up 1:1, in order, with the test set."""
    block = predictions[predictions["Balancing"] == balancing]
    if len(block) != len(test):
        raise GateFailure(
            f"alignment[{balancing}]: {len(block)} prediction rows vs {len(test)} test rows"
        )
    if not (block["Actual"].values == test["Class"].values).all():
        raise GateFailure(f"alignment[{balancing}]: Actual labels differ from test labels in order")
    print(f"  ok  alignment[{balancing}]: {len(block)} rows match test order")


def check_close(name: str, got: np.ndarray, want: np.ndarray, atol: float) -> None:
    got, want = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    if got.shape != want.shape:
        raise GateFailure(f"{name}: shape {got.shape} vs {want.shape}")
    worst = float(np.max(np.abs(got - want))) if got.size else 0.0
    if worst > atol:
        raise GateFailure(f"{name}: max abs difference {worst:.3g} exceeds {atol:g}")
    print(f"  ok  {name}: max abs difference {worst:.3g} (limit {atol:g})")


def check_metrics_row(name: str, got: dict, results_row: pd.Series, decimals: int = 4) -> None:
    """Compare Precision/Recall/F1 Score/ROC AUC to a row of the paper's results CSV."""
    for key in ("Precision", "Recall", "F1 Score", "ROC AUC"):
        if key not in got:
            continue
        a, b = round(float(got[key]), decimals), round(float(results_row[key]), decimals)
        if a != b:
            raise GateFailure(f"{name}: {key} {a} != paper {b}")
    print(f"  ok  {name}: metrics match paper to {decimals} decimals")


def git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=config.REPO_ROOT, capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def update_provenance(key: str, entry: dict) -> None:
    """Merge one entry into artifacts/provenance.json (stamped with date and commit)."""
    path = config.ARTIFACT_DIR / "provenance.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    entry = dict(entry)
    entry["trained_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry["git_commit"] = git_commit()
    data[key] = entry
    config.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
