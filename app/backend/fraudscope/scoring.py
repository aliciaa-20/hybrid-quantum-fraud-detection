"""Scoring functions. Each takes raw (unscaled) feature rows, shape (n, 4), in config.FEATURES order."""

from typing import NamedTuple

import numpy as np
import pandas as pd

from fraudscope import config
from fraudscope.registry import Registry


class ModelOutput(NamedTuple):
    labels: np.ndarray  # int 0/1
    scores: np.ndarray  # fraud probability


def score_rf(reg: Registry, X: np.ndarray) -> ModelOutput:
    scores = reg.rf.predict_proba(pd.DataFrame(X, columns=config.FEATURES))[:, 1]
    return ModelOutput((scores > config.RF_THRESHOLD).astype(int), scores)


def score_qsvm(reg: Registry, X: np.ndarray) -> ModelOutput:
    Xs = reg.qsvm["scaler"].transform(X)
    K = reg.kernel.evaluate(x_vec=Xs, y_vec=reg.qsvm["train_points"])
    svc = reg.qsvm["svc"]
    return ModelOutput(svc.predict(K).astype(int), svc.predict_proba(K)[:, 1])


def score_vqc(reg: Registry, X: np.ndarray) -> ModelOutput:
    Xs = reg.vqc_scaler.transform(X)
    proba = np.asarray(reg.vqc.predict_proba(Xs))
    scores = proba[:, 1] if proba.ndim == 2 else proba.ravel()
    labels = np.asarray(reg.vqc.predict(Xs)).ravel().astype(int)
    return ModelOutput(labels, scores)
