# Stages: web app ("Nice Try")

Plan: `docs/superpowers/plans/2026-11-11-fraudscope-app.md`
Spec: `docs/superpowers/specs/2026-11-11-fraudscope-app-design.md`
Branch: `feature/fraudscope-app`. Research-phase tracking stays in `PHASES.md`.

Status: not started / in progress / done

- [x] **Stage 1: Foundations** (done): tracker, `.venv`, approved deps, `app/backend` skeleton and config.
- [x] **Stage 2: Reproduction gate + RF export** (done): retrain Random Forest, refuse to save unless it reproduces the paper.
- [x] **Stage 3: Quantum export + sample table** (done): QSVM and VQC artifacts, 250-row sample set, provenance.
- [x] **Stage 4: Scoring API + upload validation** (done): FastAPI routes, caps, live fallback.
- [x] **Stage 5: Findings endpoint** (done): results tables from the CSVs with scope labels and caveats.
- [x] **Stage 6: Frontend scaffold + landing page** (done; visual check at 375px/1280px still to be eyeballed by the user, browser extension was not connected): Vite/React/TS, editorial style, cold-start banner.
- [x] **Stage 7: Explore, Upload, Findings, About pages** (done; browser-based visual check still pending, extension not connected).
- [x] **Stage 9: Restyle ("Nice Try", dark cosmic + motion)** (done, user-requested): replaces the editorial look; frontend only.
- [~] **Stage 8: Hosting decision + deployment + live verification** (in progress: config written; branch pushed; waiting on user to create Render and Vercel accounts).

## Notes
- Python 3.14.7 in `.venv/` (gitignored); Node v24.16.0.
- Pinned new deps: fastapi 0.162.4, uvicorn 0.54.0, python-multipart 0.0.33 (pydantic 2.14.3 comes with fastapi).
- No new test suite (user rule); verification is by runnable commands in the plan.

- Stage 3 results: QSVM labels identical to paper on 250/250 rows; VQC re-run (seed 42) full-test F1 0.0220 and ROC AUC 0.7967, inside the paper 5-seed range; live VQC agrees with the paper stored label on 241/250 sample rows.
- Stage 4 measured caps (local): QSVM 25 rows ~9.3s (cap 25), VQC 200 rows ~0.7s (cap 200); live timeout 20s (env LIVE_TIMEOUT_S). Task 8 re-measures on the host.
- Stage 8 measurements: backend peak RSS ~193 MB after a live QSVM + 25-row quantum upload (Render free = 512 MB, 0.1 CPU). Hugging Face Docker Spaces need a paid plan to create, so Render is the free choice. 0.1 CPU is the risk: quantum latency must be re-measured on the host and caps lowered.
