"""Reads the paper's results CSVs into labelled tables for the Findings page. Values are never recomputed."""

import pandas as pd

from fraudscope import config

TUNED_CAVEAT = "Best-F1 thresholds were selected using the test labels, so these figures are optimistic."  # see "validated" for the honest version


def _table(rel: str, scope: str, caveat: str | None = None, optional: bool = False) -> dict:
    path = config.RESULTS_DIR / rel
    if optional and not path.exists():  # the UI hides sections whose table is empty
        return {"rows": [], "scope": scope, "caveat": caveat}
    # keep_default_na=False: the balancing label "None" must stay a string.
    df = pd.read_csv(path, keep_default_na=False)
    return {"rows": df.to_dict(orient="records"), "scope": scope, "caveat": caveat}


def load_findings() -> dict:
    return {
        "classical_quantum": _table("final_results.csv", "full test set (56,746 rows)"),
        "cost_benefit": _table(
            "novelty/cost_benefit.csv", "full test set (56,746 rows); 'Best-F1' rows use a tuned threshold",
            TUNED_CAVEAT),
        "qsvm_vs_vqc": _table("novelty/qsvm_vs_vqc.csv", "matched 250-row class-enriched subset",
                              "This subset is 38% fraud (real-world rate is about 0.17%), so these numbers "
                              "are not comparable to full-test-set numbers. VQC training is not seeded, so its "
                              "numbers move between runs: the paper's first run scored F1 0.67 / 0.64 / 0.54 "
                              "(none / SMOTE / ADASYN); the rerun shown here scored 0.62 / 0.62 / 0.51. "
                              "QSVM is deterministic and reproduces exactly."),
        "thresholds": _table("novelty/threshold_optimization.csv", "full test set (56,746 rows)", TUNED_CAVEAT),
        "validated": _table(
            "novelty/threshold_validation.csv", "full test set (56,746 rows); cut-off chosen on held-out validation data",
            "Models were refit on 80% of the training data so a validation split could be held out, so these figures "
            "differ slightly from the main table. VQC uses a seeded run and the paper's quantum training subsets.",
            optional=True),
    }
