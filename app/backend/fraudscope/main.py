"""FastAPI app: scoring, samples, upload."""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fraudscope import config, scoring
from fraudscope.registry import load_registry
from fraudscope.schemas import LiveOut, ModelScore, SampleOut, ScoreOut, ScoreRow
from fraudscope.uploads import UploadError, parse_upload

# Quantum simulation is CPU-bound; a small pool keeps a timed-out job from blocking everything.
_pool = ThreadPoolExecutor(max_workers=2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    reg = load_registry()
    X = np.array([[s["features"][f] for f in config.FEATURES] for s in reg.samples])
    rf = scoring.score_rf(reg, X)
    for s, label, score in zip(reg.samples, rf.labels, rf.scores):
        s["rf"] = {"label": int(label), "score": float(score), "source": "live"}
        s["qsvm"]["source"] = "stored"
        s["vqc_paper"]["source"] = "stored"
    app.state.reg = reg
    yield


app = FastAPI(title="FraudScope API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(UploadError)
async def upload_error_handler(_, exc: UploadError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


async def _run_timed(fn, *args):
    """Run a blocking scoring call in the pool with the live timeout."""
    loop = asyncio.get_running_loop()
    return await asyncio.wait_for(loop.run_in_executor(_pool, fn, *args), timeout=config.LIVE_TIMEOUT_S)


def _one(out: scoring.ModelOutput, i: int, source: str = "live") -> ModelScore:
    return ModelScore(label=int(out.labels[i]), score=float(out.scores[i]), source=source)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    reg = app.state.reg
    return {
        "provenance": reg.provenance,
        "rf_threshold": config.RF_THRESHOLD,
        "caps": {"rf": config.RF_MAX_ROWS, "qsvm": config.QSVM_MAX_ROWS, "vqc": config.VQC_MAX_ROWS},
        "sample_scope": "matched 250-row class-enriched subset (95 fraud + 155 legitimate)",
    }


@app.get("/api/samples", response_model=list[SampleOut])
def samples():
    return app.state.reg.samples


@app.post("/api/samples/{sample_id}/live", response_model=LiveOut)
async def live(sample_id: int):
    reg = app.state.reg
    if not 0 <= sample_id < len(reg.samples):
        return JSONResponse(status_code=404, content={"detail": f"No sample {sample_id}."})
    s = reg.samples[sample_id]
    X = np.array([[s["features"][f] for f in config.FEATURES]])
    notes: list[str] = []
    results = {}
    for key, fn, stored in (("qsvm", scoring.score_qsvm, s["qsvm"]), ("vqc_live", scoring.score_vqc, s["vqc_paper"])):
        try:
            results[key] = _one(await _run_timed(fn, reg, X), 0)
        except Exception as e:
            reason = "took too long" if isinstance(e, asyncio.TimeoutError) else "failed"
            notes.append(f"Live {key.replace('_live', '').upper()} {reason}; showing the stored score instead.")
            results[key] = ModelScore(label=stored["label"], score=stored["score"], source="stored")
    if results["vqc_live"].source == "live":
        notes.append("Live VQC is a seeded re-run; VQC training is stochastic, so it can differ slightly "
                     "from the paper's stored run.")
    return LiveOut(notes=notes, **results)


@app.post("/api/score", response_model=ScoreOut)
async def score(file: UploadFile = File(...)):
    raw = await file.read(config.MAX_UPLOAD_BYTES + 1)
    ranges = app.state.reg.provenance.get("feature_ranges", {}).get("train_min_max")
    df, warns = parse_upload(raw, ranges)
    reg = app.state.reg
    X = df[config.FEATURES].to_numpy()
    n = len(df)
    notes: list[str] = []

    rf = scoring.score_rf(reg, X)
    quantum: dict[str, scoring.ModelOutput | None] = {"qsvm": None, "vqc": None}
    for key, fn, cap, name in (("qsvm", scoring.score_qsvm, config.QSVM_MAX_ROWS, "QSVM"),
                               ("vqc", scoring.score_vqc, config.VQC_MAX_ROWS, "VQC")):
        if n > cap:
            notes.append(f"{name} (experimental, simulated) runs on at most {cap} rows; this file has {n}, "
                         f"so only Random Forest scored it.")
            continue
        try:
            quantum[key] = await _run_timed(fn, reg, X)
        except Exception as e:
            reason = "timed out" if isinstance(e, asyncio.TimeoutError) else "failed"
            notes.append(f"{name} {reason}; Random Forest results are shown.")

    rows = [
        ScoreRow(
            row=i + 1,
            features={f: float(df.loc[i, f]) for f in config.FEATURES},
            rf=_one(rf, i),
            qsvm=_one(quantum["qsvm"], i) if quantum["qsvm"] else None,
            vqc=_one(quantum["vqc"], i) if quantum["vqc"] else None,
            warnings=[w for w in warns[i].split("; ") if w],
        )
        for i in range(n)
    ]
    return ScoreOut(rows=rows, notes=notes,
                    caps={"rf": config.RF_MAX_ROWS, "qsvm": config.QSVM_MAX_ROWS, "vqc": config.VQC_MAX_ROWS})
