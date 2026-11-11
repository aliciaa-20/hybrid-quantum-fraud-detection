"""
Phase 11b: decision-threshold selection WITHOUT test-set leakage.

Phase 1 picked each model's best-F1 threshold using the test labels, which makes the tuned numbers optimistic.
Here the threshold is chosen on held-out VALIDATION data and then applied, unchanged, to the test set.

Protocol
  - 20% of the training set is held out as validation (stratified, so it keeps the 0.17% fraud rate); the models are
    fitted on the other 80%. Balancing (SMOTE/ADASYN) is applied to the 80% only.
  - Classical models use the same settings as src/classical_models.py.
  - VQC uses the paper's quantum training subsets (data/quantum_*.csv), seeded (seed 42). Its validation set is the
    held-out rows that are NOT part of those subsets, so no VQC training row is ever used for threshold selection.
  - Reported per model x balancing: test metrics at 0.5, at the validation-chosen threshold, and the old test-tuned
    best F1 for comparison ("optimism" = old minus new).
Output: results/novelty/threshold_validation.csv (written incrementally).
"""

import time
import numpy as np
import pandas as pd
from imblearn.over_sampling import ADASYN, SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from qiskit.circuit.library import real_amplitudes, zz_feature_map
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA
from qiskit_machine_learning.utils import algorithm_globals

RS = 42
F = ["V10", "V12", "V14", "V17"]
AVG_FRAUD_AMOUNT, INVESTIGATION_COST = 122.21, 25.0  # same illustrative cost model as Phase 9
OUT = "results/novelty/threshold_validation.csv"

train = pd.read_csv("data/train_selected.csv")
test = pd.read_csv("data/test_selected.csv")
X_test, y_test = test[F], test["Class"].values
fit_df, val_df = train_test_split(train, test_size=0.2, stratify=train["Class"], random_state=RS)
X_val, y_val = val_df[F], val_df["Class"].values
old = pd.read_csv("results/novelty/threshold_optimization.csv", keep_default_na=False)
print(f"fit {len(fit_df):,} rows ({int(fit_df.Class.sum())} fraud) | val {len(val_df):,} ({int(y_val.sum())} fraud) | test {len(test):,} ({int(y_test.sum())} fraud)", flush=True)

rows = []


def best_f1_threshold(y_true, y_score):  # identical to src/novelty/threshold_optimization.py
    thresholds = np.unique(y_score)
    thresholds = thresholds[(thresholds > 0) & (thresholds < 1)]
    if len(thresholds) > 2000:
        thresholds = np.quantile(thresholds, np.linspace(0, 1, 2000))
    best_t, best_f1 = 0.5, -1
    for t in thresholds:
        f1 = f1_score(y_true, (y_score >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return best_t


def record(model, balancing, p_val, y_val_used, p_test):
    t = best_f1_threshold(y_val_used, p_val)
    at = lambda th: (p_test >= th).astype(int)
    pred = at(t)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    o = old[(old["Model"] == model) & (old["Balancing"] == balancing)]
    old_f1 = float(o["Best-F1 F1"].iloc[0]) if len(o) else np.nan
    new_f1 = f1_score(y_test, pred, zero_division=0)
    rows.append({
        "Model": model, "Balancing": balancing, "Validation Fraud Rows": int(y_val_used.sum()),
        "Validation Threshold": t,
        "Test F1 @0.5": f1_score(y_test, at(0.5), zero_division=0),
        "Test Precision @val": precision_score(y_test, pred, zero_division=0),
        "Test Recall @val": recall_score(y_test, pred, zero_division=0),
        "Test F1 @val": new_f1, "TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn),
        "Net Benefit ($) @val": tp * AVG_FRAUD_AMOUNT - fp * INVESTIGATION_COST,
        "Old Test-Tuned F1": old_f1, "Optimism (old - new)": old_f1 - new_f1,
    })
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"{model:20s} {balancing:7s} val-thr={t:.4f}  F1@0.5={rows[-1]['Test F1 @0.5']:.4f}  F1@val={new_f1:.4f}  old test-tuned={old_f1:.4f}", flush=True)


def balanced(name):
    X, y = fit_df[F], fit_df["Class"]
    if name == "None":
        return fit_df
    res = (SMOTE if name == "SMOTE" else ADASYN)(random_state=RS)
    Xr, yr = res.fit_resample(X, y)
    out = pd.DataFrame(Xr, columns=F)
    out["Class"] = yr.values
    return out


def svm_subset(data, name):  # same rule as src/classical_models.py
    legit = data[data["Class"] == 0].sample(n=min(20000, int((data["Class"] == 0).sum())), random_state=RS)
    fraud = data[data["Class"] == 1]
    if name != "None":
        fraud = fraud.sample(n=min(20000, len(fraud)), random_state=RS)
    return pd.concat([legit, fraud]).sample(frac=1, random_state=RS)


# ---------------- classical models ----------------
for name in ["None", "SMOTE", "ADASYN"]:
    data = balanced(name)
    Xd, yd = data[F], data["Class"]
    for model_name, make in [
        ("Logistic Regression", lambda: LogisticRegression(max_iter=1000, random_state=RS)),
        ("Random Forest", lambda: RandomForestClassifier(n_estimators=100, max_depth=10, random_state=RS, n_jobs=-1)),
        ("SVM", lambda: SVC(kernel="rbf", probability=True, random_state=RS)),
    ]:
        m = make()
        if model_name == "SVM":
            sub = svm_subset(data, name)
            m.fit(sub[F], sub["Class"])
        else:
            m.fit(Xd, yd)
        record(model_name, name, m.predict_proba(X_val)[:, 1], y_val, m.predict_proba(X_test)[:, 1])

# ---------------- VQC (seeded, paper's quantum training subsets) ----------------
qnone = pd.read_csv("data/quantum_none.csv")
in_quantum_train = val_df.set_index(F).index.isin(qnone.set_index(F).index)
val_vqc = val_df[~in_quantum_train]
print(f"VQC validation: {len(val_vqc):,} rows ({int(val_vqc.Class.sum())} fraud) after removing rows used to train the VQC subsets", flush=True)
for name, path in [("None", "data/quantum_none.csv"), ("SMOTE", "data/quantum_smote.csv"), ("ADASYN", "data/quantum_adasyn.csv")]:
    qt = pd.read_csv(path)
    sc = MinMaxScaler(feature_range=(-np.pi, np.pi))
    Xq = sc.fit_transform(qt[F].values)
    algorithm_globals.random_seed = RS
    vqc = VQC(feature_map=zz_feature_map(4, reps=2, entanglement="linear"),
              ansatz=real_amplitudes(4, reps=2, entanglement="linear"), optimizer=COBYLA(maxiter=30))
    t0 = time.time(); vqc.fit(Xq, qt["Class"].values)
    prob = lambda X: np.asarray(vqc.predict_proba(sc.transform(X.values)))[:, 1]
    p_val, p_test = prob(val_vqc[F]), prob(X_test)
    print(f"  VQC {name}: trained+predicted in {time.time() - t0:.0f}s", flush=True)
    record("VQC", name, p_val, val_vqc["Class"].values, p_test)
print("DONE", flush=True)
