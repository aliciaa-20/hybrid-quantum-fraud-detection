import os
import pandas as pd

print("\n" + "=" * 70)
print(" HYBRID QUANTUM MACHINE LEARNING FOR CREDIT CARD FRAUD DETECTION")
print("=" * 70)

# ---------------------------------------------------------
# 1. DATASET INFORMATION
# ---------------------------------------------------------

print("\n[1] DATASET")
print("-" * 50)

DATASET = "data/creditcard.csv"

if os.path.exists(DATASET):
    df = pd.read_csv(DATASET)

    print(f"Dataset shape       : {df.shape}")
    print(f"Total transactions  : {len(df):,}")

    if "Class" in df.columns:
        fraud = (df["Class"] == 1).sum()
        legit = (df["Class"] == 0).sum()

        print(f"Legitimate          : {legit:,}")
        print(f"Fraudulent          : {fraud:,}")
        print(f"Fraud percentage    : {fraud / len(df) * 100:.2f}%")
else:
    print("Dataset not found.")
    print("Expected location: data/creditcard.csv")
    print("Using project-known dataset information instead.")

    print("Total transactions  : 284,807")
    print("Legitimate          : 284,315")
    print("Fraudulent          : 492")
    print("Fraud percentage    : 0.17%")


# ---------------------------------------------------------
# 2. FEATURE SELECTION
# ---------------------------------------------------------

print("\n[2] FEATURE SELECTION")
print("-" * 50)

selected_features = ["V10", "V12", "V14", "V17"]

print("Method              : Mutual Information")
print("Original features   : 30")
print("Selected features   :", selected_features)
print("Number selected     :", len(selected_features))


# ---------------------------------------------------------
# 3. CLASS BALANCING
# ---------------------------------------------------------

print("\n[3] CLASS BALANCING")
print("-" * 50)

print("Configurations:")
print("  1. None")
print("  2. SMOTE")
print("  3. ADASYN")

print("\nBalancing is applied ONLY to the training data.")
print("The test set remains untouched.")


# ---------------------------------------------------------
# 4. QUANTUM MODEL
# ---------------------------------------------------------

print("\n[4] QUANTUM MODEL")
print("-" * 50)

print("Model               : Variational Quantum Classifier")
print("Qubits              : 4")
print("Input features      : 4")
print("Feature Map         : ZZFeatureMap")
print("Feature Map reps    : 2")
print("Entanglement        : Linear")
print("Ansatz              : RealAmplitudes")
print("Ansatz reps         : 2")
print("Optimizer           : COBYLA")
print("Maximum iterations  : 30")


# ---------------------------------------------------------
# 5. CLASSICAL RESULTS
# ---------------------------------------------------------

print("\n[5] CLASSICAL MODEL RESULTS")
print("-" * 50)

classical_file = "results/classical_results.csv"

if os.path.exists(classical_file):

    classical = pd.read_csv(classical_file)

    print(classical.to_string(index=False))

else:

    print("Using final recorded results:\n")

    print("Random Forest + None")
    print("  Accuracy : 0.9994")
    print("  Precision: 0.8831")
    print("  Recall   : 0.7158")
    print("  F1       : 0.7907")
    print("  ROC-AUC  : 0.9449")

    print("\nSVM + None")
    print("  F1       : 0.7749")
    print("  ROC-AUC  : 0.8901")

    print("\nLogistic Regression + None")
    print("  F1       : 0.6494")
    print("  ROC-AUC  : 0.9260")


# ---------------------------------------------------------
# 6. VQC RESULTS
# ---------------------------------------------------------

print("\n[6] VQC RESULTS")
print("-" * 50)

quantum_file = "results/quantum_results.csv"

if os.path.exists(quantum_file):

    quantum = pd.read_csv(quantum_file)
    print(quantum.to_string(index=False))

else:

    print("VQC + None")
    print("  F1       : 0.0162")
    print("  ROC-AUC  : 0.7673")

    print("\nVQC + SMOTE")
    print("  F1       : 0.0234")
    print("  ROC-AUC  : 0.8165")

    print("\nVQC + ADASYN")
    print("  F1       : 0.0123")
    print("  ROC-AUC  : 0.8089")


# ---------------------------------------------------------
# 7. CONFUSION MATRIX SUMMARY
# ---------------------------------------------------------

print("\n[7] CONFUSION MATRIX")
print("-" * 50)

print("Random Forest + None")
print("  True Negatives  : 56,642")
print("  False Positives : 9")
print("  False Negatives : 27")
print("  True Positives  : 68")

print("\nVQC + SMOTE")
print("  True Negatives  : 52,091")
print("  False Positives : 4,560")
print("  False Negatives : 40")
print("  True Positives  : 55")


# ---------------------------------------------------------
# 8. IMPORTANT EXTENSIONS
# ---------------------------------------------------------

print("\n[8] EXTENDED EXPERIMENTS")
print("-" * 50)

print("Threshold optimization")
print("  RF + ADASYN F1: 0.064 -> ~0.764")

print("\nQSVM vs VQC")
print("  QSVM + SMOTE F1 : ~0.843")
print("  VQC + SMOTE F1  : ~0.640 (paper run; a rerun gave 0.620, VQC is not seeded)")
print("  Note: matched class-enriched evaluation subset")

print("\nMulti-seed testing")
print("  Seeds: 42, 7, 123, 2024, 99")

print("\nQubit scaling")
print("  Tested: 2, 4, 6, 8 qubits")

print("\nNoise simulation")
print("  Noiseless F1 : ~0.0195")
print("  Noisy F1     : ~0.0157")


# ---------------------------------------------------------
# 9. FINAL CONCLUSION
# ---------------------------------------------------------

print("\n" + "=" * 70)
print(" FINAL CONCLUSION")
print("=" * 70)

print("""
1. The dataset is extremely imbalanced.
2. Mutual Information reduced 30 features to 4.
3. The 4 features were encoded into 4 qubits.
4. Classical models were used as baselines.
5. VQC was implemented using ZZFeatureMap + RealAmplitudes.
6. SMOTE and ADASYN were tested on training data.
7. Random Forest performed strongly on the original task.
8. VQC did not outperform the classical baselines.
9. QSVM performed better than VQC in the matched comparison.
10. The project does NOT claim quantum advantage.
11. The main contribution is systematic evaluation of quantum
    approaches under class imbalance.
""")

print("=" * 70)
print(" DEMO COMPLETE")
print("=" * 70)