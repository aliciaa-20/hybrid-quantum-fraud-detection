"""
Phase 9: Cost-benefit framing.

Converts confusion-matrix outcomes into an illustrative dollar impact, using
the ACTUAL average fraud transaction amount computed from the dataset
(not an assumed figure) for the benefit side, and a stated, clearly-flagged
illustrative assumption for the cost of investigating a flagged transaction
(false positive) -- there is no ground-truth investigation-cost figure in
the dataset, so this must be an assumption; it is stated explicitly so the
reader can substitute their own number.

Net benefit = (TP * avg_fraud_amount) - (FP * investigation_cost)
False negatives are NOT subtracted as a "cost" of the model (that fraud loss
happens regardless of which model is used) but are reported separately as
"fraud amount missed" for context.

Uses the full-test-set predictions only (classical_predictions.csv,
quantum_predictions.csv) -- the Phase 2 QSVM matched-subset numbers are
deliberately excluded from this analysis because that subset's ~38%
enriched fraud rate does not reflect real transaction volume/base rates,
and a dollar total computed on it would be misleading.
"""

import numpy as np
import pandas as pd

AVG_FRAUD_AMOUNT = 122.21  # computed from data/creditcard.csv, fraud-class mean 'Amount'
INVESTIGATION_COST = 25.0  # ILLUSTRATIVE assumption: cost to manually review one flagged txn

quantum = pd.read_csv("results/quantum_predictions.csv", keep_default_na=False)
quantum["Model"] = "VQC"
classical = pd.read_csv("results/novelty/classical_predictions.csv", keep_default_na=False)
thresholds = pd.read_csv("results/novelty/threshold_optimization.csv", keep_default_na=False)

combined = pd.concat(
    [
        quantum[["Model", "Balancing", "Actual", "Fraud Probability"]],
        classical[["Model", "Balancing", "Actual", "Fraud Probability"]],
    ],
    ignore_index=True,
)

rows = []

for (model, balancing), group in combined.groupby(["Model", "Balancing"]):
    y_true = group["Actual"].values
    y_score = group["Fraud Probability"].values

    thresh_row = thresholds[(thresholds["Model"] == model) & (thresholds["Balancing"] == balancing)]
    if thresh_row.empty:
        continue
    thresh_row = thresh_row.iloc[0]

    for threshold_label, threshold_value in [
        ("Default (0.5)", 0.5),
        ("Best-F1", thresh_row["Best-F1 Threshold"]),
    ]:
        y_pred = (y_score >= threshold_value).astype(int)

        tp = int(np.sum((y_pred == 1) & (y_true == 1)))
        fp = int(np.sum((y_pred == 1) & (y_true == 0)))
        fn = int(np.sum((y_pred == 0) & (y_true == 1)))
        tn = int(np.sum((y_pred == 0) & (y_true == 0)))

        fraud_caught_value = tp * AVG_FRAUD_AMOUNT
        investigation_total_cost = fp * INVESTIGATION_COST
        net_benefit = fraud_caught_value - investigation_total_cost
        fraud_missed_value = fn * AVG_FRAUD_AMOUNT

        rows.append({
            "Model": model,
            "Balancing": balancing,
            "Threshold": threshold_label,
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "Fraud Value Caught ($)": round(fraud_caught_value, 2),
            "Investigation Cost ($)": round(investigation_total_cost, 2),
            "Net Benefit ($)": round(net_benefit, 2),
            "Fraud Value Missed ($)": round(fraud_missed_value, 2),
        })

result_df = pd.DataFrame(rows).sort_values(["Model", "Balancing", "Threshold"])
result_df.to_csv("results/novelty/cost_benefit.csv", index=False)

pd.set_option("display.width", 160)
print(f"Assumptions: avg fraud amount = ${AVG_FRAUD_AMOUNT} (from data), "
      f"investigation cost = ${INVESTIGATION_COST} (illustrative)")
print(result_df.to_string(index=False))
print("\nSaved results/novelty/cost_benefit.csv")
