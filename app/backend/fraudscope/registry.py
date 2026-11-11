"""Loads the exported artifacts once at startup."""

import json
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from qiskit.circuit.library import zz_feature_map
from qiskit_machine_learning.algorithms import VQC
from qiskit_machine_learning.kernels import FidelityQuantumKernel

from fraudscope import config


@dataclass
class Registry:
    rf: object
    qsvm: dict  # {scaler, train_points, svc}
    kernel: FidelityQuantumKernel
    vqc: VQC
    vqc_scaler: object
    samples: list[dict]
    provenance: dict


def load_registry() -> Registry:
    a = config.ARTIFACT_DIR
    return Registry(
        rf=joblib.load(a / "rf.joblib"),
        qsvm=joblib.load(a / "qsvm.joblib"),
        kernel=FidelityQuantumKernel(feature_map=zz_feature_map(4, reps=2, entanglement="linear")),
        vqc=VQC.load(str(a / "vqc.model")),
        vqc_scaler=joblib.load(a / "vqc_scaler.joblib"),
        samples=json.loads((a / "samples.json").read_text()),
        provenance=json.loads((a / "provenance.json").read_text()),
    )
