"""Response models for the API."""

from pydantic import BaseModel


class ModelScore(BaseModel):
    label: int
    score: float
    source: str = "live"  # "live" or "stored"


class SampleOut(BaseModel):
    id: int
    test_index: int
    features: dict[str, float]
    actual: int
    rf: ModelScore
    qsvm: ModelScore
    vqc_paper: ModelScore


class LiveOut(BaseModel):
    qsvm: ModelScore
    vqc_live: ModelScore
    notes: list[str]


class ScoreRow(BaseModel):
    row: int
    features: dict[str, float]
    rf: ModelScore
    qsvm: ModelScore | None
    vqc: ModelScore | None
    warnings: list[str]


class ScoreOut(BaseModel):
    rows: list[ScoreRow]
    notes: list[str]
    caps: dict[str, int]
