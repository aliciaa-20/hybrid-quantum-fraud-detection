"""
Phase 6: Noise-model simulation.

All prior VQC results (original paper + Phases 1-5) used Qiskit's default
exact/noiseless sampler. Real NISQ hardware has gate and readout errors;
without a noise-aware comparison, the paper can't say anything about
real-device feasibility. This script retrains the best VQC configuration
found so far (ZZFeatureMap + RealAmplitudes, SMOTE training data -- the
same config Phase 4's ablation confirmed as best) under a depolarizing
noise model with illustrative NISQ-like error rates, and compares against
the noiseless result on the identical training/test split.

Feasibility: a small-scale timing check (n=60 train, 10 iters) showed noisy
fit+predict is NOT much slower than noiseless at 4 qubits (~3.1s fit,
~0.33s predict) -- linear extrapolation to the full problem size
(n=1800 train, 30 iters, 56,747 test) gives ~10 minutes, confirmed feasible
without a scaled-down subset.

Noise model: 0.1% depolarizing error on single-qubit gates, 1% on two-qubit
gates (cx), plus 1% bit-flip readout error -- representative, illustrative
NISQ-era error rates, not a specific hardware calibration.
"""

import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

from qiskit.circuit.library import zz_feature_map, real_amplitudes
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.optimizers import COBYLA
from qiskit_aer.primitives import SamplerV2 as AerSampler
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

N_QUBITS = 4
FEATURES = ["V10", "V12", "V14", "V17"]
MAX_ITER = 30
TRAIN_PATH = "data/quantum_smote.csv"
TEST_PATH = "data/test_selected.csv"

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

X_train_raw = train_df[FEATURES].values
y_train = train_df["Class"].values
X_test_raw = test_df[FEATURES].values
y_test = test_df["Class"].values

scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
X_train = scaler.fit_transform(X_train_raw)
X_test = scaler.transform(X_test_raw)


def build_noise_model():
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ["rz", "ry", "rx", "h", "sx"])
    nm.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ["cx"])
    readout_err = ReadoutError([[0.99, 0.01], [0.01, 0.99]])
    for q in range(N_QUBITS):
        nm.add_readout_error(readout_err, [q])
    return nm


def run(sampler, label):
    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)

    feature_map = zz_feature_map(feature_dimension=N_QUBITS, reps=2, entanglement="linear")
    ansatz = real_amplitudes(num_qubits=N_QUBITS, reps=2, entanglement="linear")

    kwargs = {"feature_map": feature_map, "ansatz": ansatz, "optimizer": COBYLA(maxiter=MAX_ITER)}
    if sampler is not None:
        kwargs["sampler"] = sampler
    vqc = VQC(**kwargs)

    t0 = time.time()
    vqc.fit(X_train, y_train)
    train_time = time.time() - t0

    t1 = time.time()
    y_pred = np.asarray(vqc.predict(X_test)).ravel().astype(int)
    predict_time = time.time() - t1

    try:
        proba = np.asarray(vqc.predict_proba(X_test))
        y_score = proba[:, 1] if proba.ndim == 2 else proba.ravel()
    except Exception:
        y_score = y_pred

    metrics = {
        "Condition": label,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1 Score": f1_score(y_test, y_pred, zero_division=0),
        "ROC AUC": roc_auc_score(y_test, y_score),
        "Training Time": train_time,
        "Predict Time": predict_time,
    }
    print(f"F1={metrics['F1 Score']:.4f}  ROC-AUC={metrics['ROC AUC']:.4f}  "
          f"train={train_time:.1f}s  predict={predict_time:.1f}s")
    return metrics


rows = []
rows.append(run(None, "Noiseless (default sampler)"))

noise_model = build_noise_model()
noisy_sampler = AerSampler(options={"backend_options": {"noise_model": noise_model}})
rows.append(run(noisy_sampler, "Noisy (0.1%/1qubit, 1%/2qubit depolarizing + 1% readout)"))

result_df = pd.DataFrame(rows)
result_df.to_csv("results/novelty/noise_simulation.csv", index=False)

print("\n" + "=" * 70)
print(result_df.round(4).to_string(index=False))
print("\nSaved results/novelty/noise_simulation.csv")
