import os
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# CREATE RESULTS DIRECTORY
# =========================================================

os.makedirs("results", exist_ok=True)


# =========================================================
# LOAD CLASSICAL RESULTS
# =========================================================

classical = pd.read_csv(
    "results/classical_results.csv"
)

# Replace missing balancing labels with "None"
classical["Balancing"] = (
    classical["Balancing"]
    .fillna("None")
)


# =========================================================
# LOAD OFFICIAL QUANTUM RESULTS
# =========================================================

quantum = pd.read_csv(
    "results/quantum_results.csv"
)

# Replace missing balancing labels with "None"
quantum["Balancing"] = (
    quantum["Balancing"]
    .fillna("None")
)


# =========================================================
# COMBINE CLASSICAL AND QUANTUM RESULTS
# =========================================================

final_results = pd.concat(
    [classical, quantum],
    ignore_index=True
)


# =========================================================
# SORT BY F1 SCORE
# =========================================================

final_results = final_results.sort_values(
    by="F1 Score",
    ascending=False
).reset_index(drop=True)


# =========================================================
# SAVE FINAL RESULTS
# =========================================================

final_results.to_csv(
    "results/final_results.csv",
    index=False
)


# =========================================================
# DISPLAY FINAL RESULTS
# =========================================================

print("=" * 90)
print("FINAL MODEL COMPARISON")
print("=" * 90)

print(
    final_results.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# =========================================================
# FIND BEST MODELS
# =========================================================

best_f1 = final_results.loc[
    final_results["F1 Score"].idxmax()
]

best_roc = final_results.loc[
    final_results["ROC AUC"].idxmax()
]

best_recall = final_results.loc[
    final_results["Recall"].idxmax()
]


# =========================================================
# DISPLAY BEST MODELS
# =========================================================

print("\n" + "=" * 90)
print("BEST MODELS")
print("=" * 90)

print(
    f"\nBest F1:"
    f" {best_f1['Model']} + {best_f1['Balancing']}"
    f" ({best_f1['F1 Score']:.4f})"
)

print(
    f"Best ROC AUC:"
    f" {best_roc['Model']} + {best_roc['Balancing']}"
    f" ({best_roc['ROC AUC']:.4f})"
)

print(
    f"Best Recall:"
    f" {best_recall['Model']} + {best_recall['Balancing']}"
    f" ({best_recall['Recall']:.4f})"
)


# =========================================================
# CREATE GRAPH LABELS
# =========================================================

labels = (
    final_results["Model"]
    + " + "
    + final_results["Balancing"]
)

x = range(len(final_results))


# =========================================================
# F1 SCORE COMPARISON
# =========================================================

plt.figure(figsize=(14, 7))

plt.bar(
    x,
    final_results["F1 Score"]
)

plt.xticks(
    x,
    labels,
    rotation=45,
    ha="right"
)

plt.ylabel("F1 Score")
plt.xlabel("Model Configuration")
plt.title(
    "F1 Score Comparison of Classical and Quantum Models"
)

plt.tight_layout()

plt.savefig(
    "results/model_comparison.png",
    dpi=300
)

plt.close()


# =========================================================
# ROC AUC COMPARISON
# =========================================================

plt.figure(figsize=(14, 7))

plt.bar(
    x,
    final_results["ROC AUC"]
)

plt.xticks(
    x,
    labels,
    rotation=45,
    ha="right"
)

plt.ylabel("ROC AUC")
plt.xlabel("Model Configuration")
plt.title(
    "ROC AUC Comparison of Classical and Quantum Models"
)

plt.tight_layout()

plt.savefig(
    "results/roc_auc_comparison.png",
    dpi=300
)

plt.close()


# =========================================================
# RECALL COMPARISON
# =========================================================

plt.figure(figsize=(14, 7))

plt.bar(
    x,
    final_results["Recall"]
)

plt.xticks(
    x,
    labels,
    rotation=45,
    ha="right"
)

plt.ylabel("Recall")
plt.xlabel("Model Configuration")
plt.title(
    "Fraud Detection Recall Comparison"
)

plt.tight_layout()

plt.savefig(
    "results/recall_comparison.png",
    dpi=300
)

plt.close()


# =========================================================
# PRECISION COMPARISON
# =========================================================

plt.figure(figsize=(14, 7))

plt.bar(
    x,
    final_results["Precision"]
)

plt.xticks(
    x,
    labels,
    rotation=45,
    ha="right"
)

plt.ylabel("Precision")
plt.xlabel("Model Configuration")
plt.title(
    "Precision Comparison of Classical and Quantum Models"
)

plt.tight_layout()

plt.savefig(
    "results/precision_comparison.png",
    dpi=300
)

plt.close()


# =========================================================
# TRAINING TIME COMPARISON
# =========================================================

plt.figure(figsize=(14, 7))

plt.bar(
    x,
    final_results["Training Time"]
)

plt.xticks(
    x,
    labels,
    rotation=45,
    ha="right"
)

plt.ylabel("Training Time (seconds)")
plt.xlabel("Model Configuration")
plt.title(
    "Training Time Comparison"
)

plt.tight_layout()

plt.savefig(
    "results/training_time_comparison.png",
    dpi=300
)

plt.close()


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n" + "=" * 90)
print("FILES GENERATED")
print("=" * 90)

print("results/final_results.csv")
print("results/model_comparison.png")
print("results/roc_auc_comparison.png")
print("results/recall_comparison.png")
print("results/precision_comparison.png")
print("results/training_time_comparison.png")

print("\nFinal comparison completed successfully.")