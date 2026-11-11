"""Retrain the served Random Forest (no balancing), run the reproduction gate, then save it.

Run from app/backend:  ../../.venv/bin/python -m export.export_rf
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

from export import gate
from fraudscope import config

# RF_PARAMS must match src/classical_models.py exactly.
RF_PARAMS = dict(n_estimators=100, max_depth=10, random_state=config.RANDOM_STATE, n_jobs=-1)


def main() -> None:
    train = pd.read_csv(config.DATA_DIR / "train_selected.csv")
    test = gate.load_test()
    X_train, y_train = train[config.FEATURES], train["Class"]
    X_test = test[config.FEATURES]

    print("Training Random Forest + None ...")
    model = RandomForestClassifier(**RF_PARAMS)
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    labels = (proba > config.RF_THRESHOLD).astype(int)

    print("Reproduction gate:")
    classical = gate.read_results_csv(config.SOURCE_RESULTS_DIR / "novelty" / "classical_predictions.csv")
    rf_rows = classical[classical["Model"] == "Random Forest"]
    gate.check_alignment(test, rf_rows, "None")
    stored = rf_rows[rf_rows["Balancing"] == "None"]["Fraud Probability"].values
    gate.check_close("RF/None probabilities vs paper", proba, stored, atol=1e-6)

    final = gate.read_results_csv(config.SOURCE_RESULTS_DIR / "final_results.csv")
    row = final[(final["Model"] == "Random Forest") & (final["Balancing"] == "None")].iloc[0]
    y = test["Class"].values
    gate.check_metrics_row(
        "RF/None metrics",
        {
            "Precision": precision_score(y, model.predict(X_test), zero_division=0),
            "Recall": recall_score(y, model.predict(X_test), zero_division=0),
            "F1 Score": f1_score(y, model.predict(X_test), zero_division=0),
            "ROC AUC": roc_auc_score(y, proba),
        },
        row,
    )
    if not (labels == model.predict(X_test)).all():
        raise gate.GateFailure("app labels (score > threshold) differ from model.predict")
    print("  ok  app labels equal model.predict for all rows")

    config.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.ARTIFACT_DIR / "rf.joblib", compress=3)

    ranges = {f: [float(train[f].min()), float(train[f].max())] for f in config.FEATURES}
    gate.update_provenance("random_forest", {
        "model": "Random Forest", "balancing": "None", "seed": config.RANDOM_STATE,
        "threshold": config.RF_THRESHOLD, "params": {k: v for k, v in RF_PARAMS.items()},
        "gate": "passed", "gate_details": "probabilities atol 1e-6; metrics 4dp; alignment; labels",
    })
    gate.update_provenance("feature_ranges", {"train_min_max": ranges, "source": "data/train_selected.csv"})
    size_mb = (config.ARTIFACT_DIR / "rf.joblib").stat().st_size / 1e6
    print(f"saved artifacts/rf.joblib ({size_mb:.1f} MB)")
    if size_mb > 50:
        print("WARNING: rf.joblib exceeds 50 MB; stop and ask the user before continuing.")


if __name__ == "__main__":
    main()
