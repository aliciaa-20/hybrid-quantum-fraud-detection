# FraudScope Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the honors fraud-detection research into a public, free-hosted web app where examiners browse real test transactions, upload small CSVs, and compare Random Forest, QSVM and VQC, with every number traceable to the paper's results.

**Architecture:** A FastAPI backend loads three exported models and a precomputed table of 250 sample transactions at startup, and serves scoring and findings endpoints. A React (Vite, TypeScript) frontend with a story-first editorial landing page calls it. A one-time export step retrains the models and refuses to ship them unless they reproduce the paper's results.

**Tech Stack:** Python (FastAPI, uvicorn, scikit-learn, qiskit, qiskit-machine-learning, pandas, joblib), React + Vite + TypeScript, Vercel (frontend), Render or Hugging Face Spaces (backend, decided in Task 8).

**Spec:** `docs/superpowers/specs/2026-11-11-fraudscope-app-design.md`

## Decisions made while planning (please check)

1. **No new test suite.** Your global rule says no new tests unless you ask. So every task is verified by a runnable command with an expected output (the reproduction gate is a script, not a test suite). Say the word and I will add pytest tests.
2. **Sample set = the paper's matched 250-row evaluation subset** (all 95 test-set frauds + 155 legitimate, rebuilt with `random_state=42` exactly as `src/novelty/qsvm_kernel.py` does). Reason: QSVM was only ever evaluated there, so all three models have comparable numbers on it. It is class-enriched (38% fraud), so the UI must say so.
3. **Served models:** Random Forest trained on no-balancing data (`train_selected.csv`) at threshold 0.5. This avoids the problem that the best-F1 thresholds were tuned on the test labels (confirmed in `src/novelty/threshold_optimization.py`). QSVM and VQC use SMOTE data, the paper's headline quantum configuration.
4. **VQC has two scores.** The paper's VQC weights were never saved and training was not seeded, so the exact paper model cannot be rebuilt. The sample browser shows the paper run's stored VQC output (from `results/quantum_predictions.csv`). "Run live" uses a re-trained, seeded VQC and shows its score beside the stored one with an explanation. Both are real model outputs; neither is invented.
5. **QSVM is re-run, not copied.** The stored CSV has only hard labels for QSVM, so Task 3 re-trains it (seeded, deterministic) to get probabilities, and checks its labels equal the stored ones.

## Global Constraints

- No hardcoded secrets; `.env` in `.gitignore`.
- Never install a dependency without the user's approval (Task 1 collects it once for the whole list).
- Never commit `data/*.csv` (gitignored). Committed artifacts live under `app/backend/artifacts/`.
- Work on branch `feature/fraudscope-app`; never commit to `main`; ask before any push; never force-push.
- Commit after each completed task; update `STAGES.md` and `README.md` in the same task.
- A task is done only when it builds/runs and its verification commands pass.
- Hyperparameters, seeds, features and preprocessing must match `src/` exactly: `RANDOM_STATE=42`; features `["V10","V12","V14","V17"]`; RF `n_estimators=100, max_depth=10, n_jobs=-1`; scaler `MinMaxScaler(feature_range=(-np.pi, np.pi))`; `zz_feature_map(feature_dimension=4, reps=2, entanglement="linear")`; `real_amplitudes(num_qubits=4, reps=2, entanglement="linear")`; `COBYLA(maxiter=30)`; QSVM train subset 120 rows (60 fraud + 60 legit), eval subset 250 rows (95 fraud + 155 legit).
- Never lead with accuracy anywhere in the UI; show precision, recall, F1, ROC-AUC and confusion counts.
- QSVM's matched-subset numbers must always carry the label "matched 250-row class-enriched subset" and never appear unlabelled beside full-test-set numbers.
- Never claim quantum advantage in any copy.
- Quantum models are labelled "experimental". Uploads are scored and discarded, never stored.

## Review Focus

- Upload CSV with missing, misnamed, duplicated or non-numeric feature columns, NaN/inf, empty file, BOM or oversized file: clear 4xx message naming the problem; never a 500, never silently scoring the wrong columns. (Task 4)
- Upload larger than a quantum cap: RF scores every row, quantum is skipped with a visible note, request does not time out. (Task 4)
- Live quantum call slow or failing: falls back to the stored score with a visible note, never a blank or spinner forever. (Tasks 4, 7)
- Backend asleep on a free tier (30-60 s cold start): the frontend shows a "waking the server" state, not an error or blank page. (Task 6)
- Uploaded feature values far outside the training range (quantum scaler extrapolates beyond [-π, π]): row is scored but flagged "outside training range". (Task 4)

---

## File structure

```
STAGES.md                                   stage tracker (Task 1)
app/backend/
  requirements.txt                          backend deps (Task 1)
  fraudscope/
    config.py                               paths, constants, caps
    schemas.py                              pydantic response models
    registry.py                             loads artifacts once at startup
    scoring.py                              score_rf / score_qsvm / score_vqc
    uploads.py                              CSV validation -> DataFrame
    findings.py                             reads results/*.csv into labelled tables
    main.py                                 FastAPI app and routes
  export/
    gate.py                                 reproduction checks (shared)
    export_rf.py                            retrain RF, run gate, save
    export_quantum.py                       retrain QSVM+VQC, build samples, gate, save
  artifacts/                                committed outputs: rf.joblib, qsvm.joblib,
                                            vqc.model, samples.json, provenance.json
app/frontend/                               Vite + React + TS (Tasks 6-7)
render.yaml (or Dockerfile)                 deployment config (Task 8)
```

---

### Task 1: Foundations, approvals and tracker

**Files:**
- Create: `STAGES.md`, `app/backend/requirements.txt`, `app/backend/fraudscope/__init__.py`, `app/backend/fraudscope/config.py`, `app/backend/export/__init__.py`
- Modify: `README.md` (add an "App" section stub), `.gitignore` (confirm `.venv/`, `.env`, `app/frontend/node_modules/`, `app/frontend/dist/`)

**Interfaces:**
- Produces (`config.py`): `REPO_ROOT: Path`, `DATA_DIR: Path`, `RESULTS_DIR: Path`, `ARTIFACT_DIR: Path`, `FEATURES: list[str]`, `RANDOM_STATE: int = 42`, `RF_THRESHOLD: float = 0.5`, `RF_MAX_ROWS: int = 50_000`, `MAX_UPLOAD_BYTES: int = 5_000_000`, `QSVM_MAX_ROWS: int`, `VQC_MAX_ROWS: int` (placeholders until Task 4 measures them).

- [ ] **Step 1: Ask the user to approve the dependency list** in one message: backend adds `fastapi`, `uvicorn`, `python-multipart` on top of the already-pinned `requirements.txt`; frontend adds `react`, `react-dom`, `react-router-dom`, `vite`, `typescript`, `@vitejs/plugin-react`. Also approve creating `.venv/` and running `npm`. Do not proceed to Step 3 without a yes.
- [ ] **Step 2: Create `STAGES.md`** with one checklist entry per task in this plan (name, one-line scope, status: not started / in progress / done). Mark Task 1 in progress.
- [ ] **Step 3: Create `.venv`, install** root `requirements.txt` plus the approved backend packages; write `app/backend/requirements.txt` listing only what the backend needs at runtime (no matplotlib, seaborn, python-docx, qiskit-aer).
- [ ] **Step 4: Write `config.py`** with the interface above. Path constants resolve from `Path(__file__)`, not the current directory.
- [ ] **Step 5: Verify.** Run `cd app/backend && ../../.venv/bin/python -c "from fraudscope import config; print(config.DATA_DIR.exists(), config.FEATURES)"`. Expected: `True ['V10', 'V12', 'V14', 'V17']`. Also run `../../.venv/bin/python -c "import qiskit_machine_learning, fastapi, sklearn"` with no error.
- [ ] **Step 6: Commit** (`Stage 1: foundations, tracker, config`) with `STAGES.md` updated to done.

---

### Task 2: Reproduction gate and Random Forest export

**Files:**
- Create: `app/backend/export/gate.py`, `app/backend/export/export_rf.py`, `app/backend/artifacts/rf.joblib`, `app/backend/artifacts/provenance.json`

**Interfaces:**
- Produces (`gate.py`):
  - `class GateFailure(Exception)`
  - `load_test() -> pd.DataFrame` (reads `data/test_selected.csv`)
  - `check_alignment(test: pd.DataFrame, predictions: pd.DataFrame, balancing: str) -> None` raises `GateFailure` if the `Actual` column of that balancing block differs from `test["Class"]` in order (or length)
  - `check_close(name: str, got: np.ndarray, want: np.ndarray, atol: float) -> None`
  - `check_metrics_row(name: str, got: dict, results_row: pd.Series, decimals: int = 4) -> None` compares Precision/Recall/F1 Score/ROC AUC against a row of `results/final_results.csv`
- Produces (`export_rf.py`): `main() -> None`; saves `rf.joblib` and appends an entry to `provenance.json` (`{model, balancing, seed, trained_at, git_commit, gate: "passed", gate_details}`).

- [ ] **Step 1: Write `gate.py`** with the interfaces above. Read CSVs with `keep_default_na=False` (the string "None" is a balancing label; pandas turns it into NaN otherwise — a bug already hit in `src/novelty`).
- [ ] **Step 2: Write `export_rf.py`.** Train `RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)` on `data/train_selected.csv`; compute probabilities on the test set.
- [ ] **Step 3: Gate in `export_rf.py` before saving:** (a) `check_alignment` on `results/novelty/classical_predictions.csv` rows `Model=="Random Forest", Balancing=="None"`; (b) `check_close` retrained probabilities against that CSV's `Fraud Probability`, `atol=1e-6`; (c) `check_metrics_row` against the `Random Forest / None` row of `results/final_results.csv`; (d) labels used by the app (`score > RF_THRESHOLD`) equal `model.predict(X_test)` for all rows. Any failure aborts without saving and prints what differed.
- [ ] **Step 4: Run** `cd app/backend && ../../.venv/bin/python -m export.export_rf`. Expected: prints each check as passed, then `saved artifacts/rf.joblib`. Record the file size; expected to be a few MB. If it is over 50 MB, stop and tell the user (do not change hyperparameters).
- [ ] **Step 5: Verify the gate can fail.** Temporarily change `max_depth` to 9, run again, and confirm it aborts with a `GateFailure` and writes nothing. Revert the change.
- [ ] **Step 6: Commit** (`Stage 2: reproduction gate and RF export`), `STAGES.md` updated.

---

### Task 3: Quantum export, sample table and provenance

**Files:**
- Create: `app/backend/export/export_quantum.py`, `app/backend/artifacts/qsvm.joblib`, `app/backend/artifacts/vqc.model`, `app/backend/artifacts/samples.json`
- Modify: `app/backend/export/gate.py` (add VQC and QSVM checks), `app/backend/artifacts/provenance.json`

**Interfaces:**
- Consumes: `gate.load_test`, `gate.check_alignment`, `config.*` from Tasks 1-2.
- Produces (`gate.py`): `build_eval_subset(test: pd.DataFrame) -> pd.DataFrame` that rebuilds the 250-row subset exactly as `src/novelty/qsvm_kernel.py` does (all frauds + `sample(n=155, random_state=42)` legit, shuffled with `random_state=42`) and keeps the original test-set index in a column `test_index`.
- Produces (`samples.json`): list of 250 objects `{id: int, test_index: int, features: {V10,V12,V14,V17: float}, actual: int, qsvm: {label: int, score: float}, vqc_paper: {label: int, score: float}}` (RF is scored live from `rf.joblib`, not stored).
- Produces (`qsvm.joblib`): dict `{scaler: MinMaxScaler, train_points: np.ndarray (120x4, scaled), svc: SVC}`.

- [ ] **Step 1: Write `build_eval_subset`** and verify its output matches `results/novelty/qsvm_vs_vqc_predictions.csv` for the `SMOTE` block: same length (250) and `Actual` equal to the subset's `Class` in order.
- [ ] **Step 2: QSVM export.** Rebuild the 120-row SMOTE training subset exactly as in `qsvm_kernel.py`, scale, compute the fidelity kernel (`FidelityQuantumKernel`), fit `SVC(kernel="precomputed", probability=True, random_state=42)`, then compute labels (`svc.predict`) and probabilities on the 250 rows. Gate: labels equal the stored `QSVM Predicted` for the SMOTE block, and F1/precision/recall equal the `QSVM / SMOTE` row of `results/novelty/qsvm_vs_vqc.csv` to 4 decimals. Expected runtime ~2-3 minutes.
- [ ] **Step 3: VQC export.** Train a seeded VQC (`algorithm_globals.random_seed = 42`) on `data/quantum_smote.csv` with the configuration in Global Constraints; save with the library's `save` (fall back to `dill` if load fails). Gate: score the 250-row subset, then check its F1 lies within the range the paper observed across seeds in `results/novelty/vqc_multiseed_summary.csv` (read that file to define exact bounds). If it falls outside, stop and tell the user rather than loosening the bound.
- [ ] **Step 4: Build `samples.json`.** For each of the 250 rows take the paper's stored VQC label and probability from `results/quantum_predictions.csv` (`Balancing=="SMOTE"`) at `test_index` (after `check_alignment` passes for that block), and QSVM from Step 2. Verify `actual` equals the test label and the file contains exactly 95 frauds.
- [ ] **Step 5: Write provenance** for QSVM and VQC (model, balancing, seed, date, git commit, gate results, and a `note` for VQC: "live model is a seeded re-run; stored scores are from the paper's run").
- [ ] **Step 6: Verify load.** Run a short script that loads all three artifacts fresh and scores the 250 rows with each. Expected: no error, QSVM live labels identical to `samples.json` labels, VQC live vs stored agreement printed (a number, not hidden).
- [ ] **Step 7: Commit** (`Stage 3: quantum export, sample table, provenance`), `STAGES.md` updated.

---

### Task 4: Scoring service, upload validation and API

**Files:**
- Create: `app/backend/fraudscope/{schemas,registry,scoring,uploads,main}.py`
- Modify: `app/backend/fraudscope/config.py` (set measured caps)

**Interfaces:**
- Consumes: artifacts and `config` from Tasks 1-3.
- Produces (`scoring.py`): `class ModelOutput(NamedTuple): labels: np.ndarray; scores: np.ndarray`, and `score_rf(reg: Registry, X: np.ndarray) -> ModelOutput`, `score_qsvm(reg, X) -> ModelOutput`, `score_vqc(reg, X) -> ModelOutput`. RF label is `score > RF_THRESHOLD`; QSVM and VQC labels come from the model's own `predict`, scores from `predict_proba[:, 1]`.
- Produces (`uploads.py`): `class UploadError(ValueError)` with a user-readable message; `parse_upload(raw: bytes) -> tuple[pd.DataFrame, list[str]]` returns the four feature columns (float) and a list of per-row warnings.
- Produces (`registry.py`): `class Registry` with `.rf`, `.qsvm`, `.vqc`, `.samples: list[dict]`, `.provenance: dict`; `load_registry() -> Registry`.
- Produces (`main.py`) routes:
  - `GET /api/health` -> `{status: "ok"}`
  - `GET /api/samples` -> sample list with live-computed RF label/score added to each stored record
  - `POST /api/samples/{id}/live` -> `{qsvm: {...}|null, vqc_live: {...}|null, notes: [str]}`; on timeout or error returns the stored scores plus a note, status 200
  - `POST /api/score` (multipart CSV) -> `{rows: [{row, features, rf, qsvm|null, vqc|null, warnings}], notes: [str], caps: {qsvm, vqc, rf}}`
  - `GET /api/meta` -> provenance, thresholds, caps

- [ ] **Step 1: Write `uploads.py`.** Strip a UTF-8 BOM, trim header whitespace, require all four feature columns exactly once (extra columns including `Class` are ignored), coerce to float, reject NaN/inf, empty, >`RF_MAX_ROWS` rows or >`MAX_UPLOAD_BYTES`; each error names the problem (for example: "Missing column V14. Found: V10, V12, V17"). Flag per-row "outside training range" when a feature lies outside the min/max seen in the training data (store these four min/max pairs in `provenance.json` during Task 3 or compute from `train_selected.csv` at export time).
- [ ] **Step 2: Write `registry.py`, `scoring.py`, `schemas.py`.** Load artifacts once; `score_qsvm` evaluates the fidelity kernel of the scaled rows against `train_points`, then `svc.predict`/`predict_proba`.
- [ ] **Step 3: Write `main.py`.** Quantum runs only if row count <= cap, else it is skipped with a note. Live calls run under a timeout (start value 20 s, constant in `config.py`) and return the stored score plus a note on timeout or exception. Set CORS from an `ALLOWED_ORIGINS` environment variable (comma-separated; default `http://localhost:5173`).
- [ ] **Step 4: Measure and set caps.** Time QSVM on 1, 10 and 25 rows and VQC on 10, 50 and 200 rows; set `QSVM_MAX_ROWS` and `VQC_MAX_ROWS` so a worst-case request finishes in under ~15 s locally (expect to halve them on a free host; Task 8 re-checks). Record the numbers in `STAGES.md`.
- [ ] **Step 5: Verify, with the server running** (`cd app/backend && ../../.venv/bin/uvicorn fraudscope.main:app --port 8000`):
  - `curl -s localhost:8000/api/health` -> `{"status":"ok"}`
  - `GET /api/samples` returns 250 items, 95 with `actual == 1`
  - A CSV missing `V14` -> HTTP 422 with message naming `V14`; empty file, a NaN value, a text value, and a CSV with a BOM each give the intended 4xx or succeed (BOM) and never a 500
  - A CSV with `cap+1` rows -> 200, RF scored for all rows, `qsvm` null, a note explaining why
  - A row with `V14 = 1e6` -> scored, warning contains "outside training range"
  - `POST /api/samples/0/live` with the quantum timeout forced to 0.001 s -> 200 with stored scores and a fallback note
- [ ] **Step 6: Commit** (`Stage 4: scoring API and upload validation`), `STAGES.md` updated.

---

### Task 5: Findings data from the results files

**Files:**
- Create: `app/backend/fraudscope/findings.py`
- Modify: `app/backend/fraudscope/main.py` (add route)

**Interfaces:**
- Consumes: `config.RESULTS_DIR`.
- Produces (`findings.py`): `load_findings() -> dict` with keys `classical_quantum` (from `results/final_results.csv`), `cost_benefit` (from `results/novelty/cost_benefit.csv`), `qsvm_vs_vqc` (from `results/novelty/qsvm_vs_vqc.csv`), `thresholds` (from `results/novelty/threshold_optimization.csv`). Each value is `{rows: list[dict], scope: str, caveat: str|None}`. The `qsvm_vs_vqc` scope is `"matched 250-row class-enriched subset"`; `thresholds` and `cost_benefit` best-F1 rows carry the caveat `"Best-F1 thresholds were selected using the test labels, so these figures are optimistic."`; `classical_quantum` scope is `"full test set (56,746 rows)"`.
- Route: `GET /api/findings` returns that dict.
- The CSV directory must be shipped with the backend deployment (copy only `results/*.csv` and `results/novelty/*.csv`, not images, into `app/backend/artifacts/results/` at build time, or set `RESULTS_DIR` accordingly).

- [ ] **Step 1: Implement `load_findings`.** Read with `keep_default_na=False`; do not round or recompute values.
- [ ] **Step 2: Add the route and a build-time copy step** (a small script `app/backend/export/copy_results.py` that copies the four CSVs into `artifacts/results/`; `config.RESULTS_DIR` points there).
- [ ] **Step 3: Verify.** `GET /api/findings` returns all four keys; the RF/None row of `classical_quantum` has F1 `0.7907` (to 4 decimals) matching `results/final_results.csv`; every row of `qsvm_vs_vqc` sits under the matched-subset scope; the best-F1 caveat is present on `thresholds`.
- [ ] **Step 4: Commit** (`Stage 5: findings endpoint`), `STAGES.md` updated.

---

### Task 6: Frontend scaffold, editorial style and landing page

**Files:**
- Create: `app/frontend/` via Vite React-TS template; `src/api.ts`, `src/styles.css`, `src/App.tsx`, `src/pages/Landing.tsx`, `src/components/ServerStatus.tsx`

**Interfaces:**
- Produces (`api.ts`): `API_BASE: string` from `import.meta.env.VITE_API_URL` (default `http://localhost:8000`); typed functions `getHealth()`, `getSamples()`, `liveScore(id)`, `scoreCsv(file)`, `getFindings()`, `getMeta()` matching the Task 4-5 response shapes.
- Produces (`ServerStatus.tsx`): hook `useServerStatus(): "waking" | "ready" | "down"`, which polls `/api/health` every 3 s until ready or a 90 s limit, and a banner component using it.

- [ ] **Step 1: Scaffold** with the approved Vite template and dependencies; add routes `/`, `/explore`, `/upload`, `/findings`, `/about` with `react-router-dom`.
- [ ] **Step 2: Style in the clean-editorial direction the user chose:** white background, one serif display face for headings plus a clean sans for body (system font stacks, no external font requests), generous spacing, one dark accent, high contrast, readable on a projector and in print. Define colors as CSS variables.
- [ ] **Step 3: Landing page.** Headline "Does quantum beat classical at catching fraud?", subline "Honest answer: not yet.", three entry points (Try a sample transaction, Upload a CSV, Read the findings), and a stat strip whose figures come from `getFindings()` (RF best net benefit vs VQC), never hard-coded.
- [ ] **Step 4: Cold-start handling.** On first render call `useServerStatus`; while `waking` show "Waking the server, this can take up to a minute on the free plan" and disable entry buttons; on `down` show a plain retry message.
- [ ] **Step 5: Verify.** `cd app/frontend && npm run build` succeeds; with the backend running, `npm run dev` shows the landing page populated from the API; with the backend stopped, the page shows the waking/down state and no console errors. Check at 375 px and 1280 px widths.
- [ ] **Step 6: Commit** (`Stage 6: frontend scaffold and landing page`), `STAGES.md` updated.

---

### Task 7: Explore, Upload, Findings and About pages

**Files:**
- Create: `src/pages/{Explore,Upload,Findings,About}.tsx`, `src/components/{ScoreCard,ConfusionTable,MetricTable}.tsx`

**Interfaces:**
- Consumes: `api.ts` functions from Task 6.
- Produces: `ScoreCard` props `{model: string, label: 0|1, score: number, experimental?: boolean, note?: string}`.

- [ ] **Step 1: Explore.** List the 250 samples with filters (All / Known fraud / Legitimate), clearly stating the set is class-enriched. Selecting one shows the four feature values, the **true label**, and a `ScoreCard` for RF, QSVM and the paper's VQC output side by side, with correct/incorrect marking per model so misses are visible. A "Run live" button calls `liveScore(id)`, shows a loading state, and renders the live QSVM and re-run VQC scores beside the stored ones with the note returned by the API (including any fallback note).
- [ ] **Step 2: Upload.** File picker for CSV (maximum size and the required columns stated up front), result table with RF verdict and score for every row and quantum columns only where present, API notes and per-row warnings shown, API 4xx messages shown verbatim. Include a download of an example CSV built from three sample rows. Nothing is stored; say so on the page.
- [ ] **Step 3: Findings.** Render `getFindings()` tables with each table's `scope` and `caveat` visible above it; lead columns are Precision, Recall, F1, ROC AUC; Accuracy is the last column in muted text with a one-line explanation of why it misleads at 0.17% fraud. Cost-benefit table highlights that every VQC row is negative.
- [ ] **Step 4: About.** Method summary (4 features by mutual information, SMOTE/ADASYN, models, simulator-only), what "experimental" means, the fact that the VQC live model is a seeded re-run, dataset attribution (ULB Machine Learning Group; confirm the licence terms on the Kaggle page before launch), and a link to the paper PDF if the user wants it public (ask).
- [ ] **Step 5: Verify against the backend.** Pick the first known-fraud sample and confirm the RF score on screen equals the `/api/samples` JSON value; upload a valid 3-row CSV, a CSV missing a column, and an over-cap CSV and confirm each behaves as in Task 4; force a live timeout (stop the backend mid-request) and confirm the stored score and note are shown; `npm run build` passes; check 375 px width.
- [ ] **Step 6: Commit** (`Stage 7: explore, upload, findings, about`), `STAGES.md` and `README.md` updated.

---

### Task 8: Hosting decision, deployment and live verification

**Files:**
- Create: `render.yaml` (or `app/backend/Dockerfile` if Hugging Face Spaces is chosen), `app/frontend/.env.example`
- Modify: `README.md` (deploy section and live URL), `STAGES.md`

**Interfaces:**
- Consumes: backend start command `uvicorn fraudscope.main:app --host 0.0.0.0 --port $PORT`; env vars `ALLOWED_ORIGINS` (backend), `VITE_API_URL` (frontend).

- [ ] **Step 1: Measure the backend's peak memory** locally (start it, call `/api/samples`, one live QSVM and one live VQC request, read the process RSS).
- [ ] **Step 2: Check current free-tier limits** for Render, Hugging Face Spaces, Vercel and Netlify by searching the web at this point (limits change), and recommend one backend host to the user: Render if peak RSS is comfortably under its free memory limit, Hugging Face Spaces (Docker) if not. Present the numbers and let the user decide.
- [ ] **Step 3: Write the deployment config** for the chosen host; set `ALLOWED_ORIGINS` to the frontend URL.
- [ ] **Step 4: Ask the user to confirm pushing** the branch to GitHub (and merging to `main` via a pull request, since the user's rules forbid committing to `main` directly), and to create the host accounts. Do not push without a yes.
- [ ] **Step 5: Deploy** backend and frontend, set env vars, and re-measure live QSVM/VQC latency on the host; lower the caps in `config.py` if needed and redeploy.
- [ ] **Step 6: Live accuracy check.** On the public URLs, confirm: RF score for the first known-fraud sample equals the local value; `/api/findings` RF/None F1 is `0.7907`; the cold-start banner appears after the service has slept; an upload of 3 rows scores correctly; a live quantum call either returns or falls back with a note.
- [ ] **Step 7: Warm-up note for the demo** in `README.md`: open the URL a few minutes before the examination; the landing page itself wakes the backend.
- [ ] **Step 8: Finish.** Update `README.md` (what it does, how to run locally, how it was deployed, live URL) and `STAGES.md`; commit (`Stage 8: deployment`); stop the visual-companion server if still running.

---

## Self-review

- **Spec coverage:** public free URL (Task 8); accuracy requirements 1-2 (Tasks 2-3), 3 (Tasks 5-7), 4 (Tasks 6-7), 5 (Task 7 Explore), 6 (Tasks 3, 5, 7), 7 (Task 5 caveat, Task 7 Findings), 8 (Tasks 3, 4, 7); sample browser, upload, findings, about (Task 7); hybrid quantum handling (Tasks 3, 4, 7); landing page and editorial style (Task 6); explanations (see gap below); free hosting and memory risk (Task 8); `STAGES.md`/README/commit conventions (every task).
- **Gap, deliberately left out:** the spec's optional RF feature-attribution explanation is not in any task. It was marked "my guess, not confirmed" and a wrong or misleading explanation would violate the accuracy goal. Add it as a Task 9 only if the user wants it (scikit-learn's built-in feature importances are global, not per-prediction, so a real per-row method needs a new dependency such as SHAP and the user's approval).
- **Type consistency:** `ModelOutput(labels, scores)` is used by all three `score_*` functions and the routes; `samples.json` field names (`qsvm`, `vqc_paper`, `test_index`) match the `/api/samples` shape and the `ScoreCard` props.
- **Proportion:** code appears only for interfaces and verification commands; bodies are left to the implementer.
