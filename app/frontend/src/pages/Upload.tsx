import { motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { getMeta, getSamples, scoreCsv } from "../api";
import type { Meta, ModelScore, Sample, ScoreResult, ScoreRow } from "../api";
import CountUp from "../components/CountUp";
import StarButton from "../components/StarButton";
import Reveal from "../components/Reveal";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";

const REQUIRED = ["V10", "V12", "V14", "V17"];

type Preview = { name: string; kb: number; rows: number; missing: string[] };

async function inspect(file: File): Promise<Preview> {
  const text = (await file.text()).replace(/^﻿/, "");
  const lines = text.split(/\r?\n/).filter((l) => l.trim() !== "");
  const header = (lines[0] ?? "").split(",").map((h) => h.trim());
  return { name: file.name, kb: Math.max(1, Math.round(file.size / 1024)), rows: Math.max(0, lines.length - 1), missing: REQUIRED.filter((c) => !header.includes(c)) };
}

const toCsv = (rows: Sample[]) =>
  ["V10,V12,V14,V17", ...rows.map((s) => REQUIRED.map((c) => s.features[c]).join(","))].join("\n") + "\n";

function Pill({ m }: { m: ModelScore | null }) {
  if (!m) return <span className="muted">—</span>;
  return <span className={`pill ${m.label === 1 ? "f" : "l"}`}>{m.label === 1 ? "Fraud" : "Legit"} {Math.round(m.score * 100)}%</span>;
}

type SortKey = "risk" | "row";

export default function Upload() {
  const status = useServerStatus();
  const [meta, setMeta] = useState<Meta | null>(null);
  const [samples, setSamples] = useState<Sample[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScoreResult | null>(null);
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [sort, setSort] = useState<SortKey>("risk");
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (status !== "ready") return;
    getMeta().then(setMeta).catch(() => setMeta(null));
    getSamples().then(setSamples).catch(() => setSamples([]));
  }, [status]);

  const choose = async (f: File | undefined | null) => {
    if (!f) return;
    setFile(f);
    setResult(null);
    setError(null);
    setPreview(await inspect(f));
  };

  const useSample = (kind: "fraud" | "legit" | "mixed") => {
    const frauds = samples.filter((s) => s.actual === 1), legit = samples.filter((s) => s.actual === 0);
    const rows = kind === "fraud" ? frauds.slice(0, 5) : kind === "legit" ? legit.slice(0, 5) : [...frauds.slice(0, 10), ...legit.slice(0, 10)];
    choose(new File([toCsv(rows)], `${kind}-sample.csv`, { type: "text/csv" }));
  };

  const run = async () => {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await scoreCsv(file));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => { setFile(null); setPreview(null); setResult(null); setError(null); if (input.current) input.current.value = ""; };

  const caps = meta?.caps;
  const plan = (cap: number | undefined) => (preview && cap !== undefined ? preview.rows <= cap : null);

  const rows = useMemo(() => {
    if (!result) return [];
    let r: ScoreRow[] = flaggedOnly ? result.rows.filter((x) => x.rf.label === 1) : [...result.rows];
    if (sort === "risk") r = r.sort((a, b) => b.rf.score - a.rf.score);
    return r;
  }, [result, flaggedOnly, sort]);

  const flagged = result ? result.rows.filter((r) => r.rf.label === 1).length : 0;
  const disagree = (r: ScoreRow) => [r.rf, r.qsvm, r.vqc].filter((m): m is ModelScore => m !== null).some((m) => m.label !== r.rf.label);

  const download = () => {
    if (!result) return;
    const head = "row,V10,V12,V14,V17,rf_label,rf_score,qsvm_label,qsvm_score,vqc_label,vqc_score";
    const lines = result.rows.map((r) => [r.row, ...REQUIRED.map((c) => r.features[c]), r.rf.label, r.rf.score.toFixed(4),
      r.qsvm?.label ?? "", r.qsvm?.score.toFixed(4) ?? "", r.vqc?.label ?? "", r.vqc?.score.toFixed(4) ?? ""].join(","));
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([[head, ...lines].join("\n") + "\n"], { type: "text/csv" }));
    a.download = "nice-try-scores.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <>
      <ServerBanner state={status} />
      <section className="page">
        <h1>Upload</h1>
        <p className="lede small-lede">
          Drop in a CSV of transactions and watch three models vote on every row. Files are scored and discarded; nothing is stored.
        </p>

        <div className="upload-grid">
          <Reveal>
            <div
              className={`dropzone ${dragging ? "over" : ""} ${preview ? "has" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => { e.preventDefault(); setDragging(false); choose(e.dataTransfer.files?.[0]); }}
            >
              <input ref={input} type="file" accept=".csv,text/csv" hidden onChange={(e) => choose(e.target.files?.[0])} />
              {!preview ? (
                <>
                  <div className="drop-icon" aria-hidden="true">⇪</div>
                  <h2>Drop a CSV here</h2>
                  <p className="muted">or</p>
                  <div className="drop-actions">
                    <StarButton onClick={() => input.current?.click()} disabled={status !== "ready"}>Choose a file</StarButton>
                  </div>
                  <p className="muted small">No file handy? Try real test-set transactions:</p>
                  <div className="drop-actions">
                    <button className="secondary" disabled={!samples.length} onClick={() => useSample("fraud")}>5 known frauds</button>
                    <button className="secondary" disabled={!samples.length} onClick={() => useSample("legit")}>5 legitimate</button>
                    <button className="secondary" disabled={!samples.length} onClick={() => useSample("mixed")}>A mix of 20</button>
                  </div>
                </>
              ) : (
                <>
                  <h2>{preview.name}</h2>
                  <p className="muted">{preview.rows.toLocaleString("en-US")} rows · {preview.kb} KB</p>
                  {preview.missing.length > 0 ? (
                    <p className="bad" role="alert">Missing column{preview.missing.length > 1 ? "s" : ""}: {preview.missing.join(", ")}. See \u201cBringing your own CSV?\u201d for the format.</p>
                  ) : (
                    <ul className="plan" aria-label="What will run">
                      <li className="ok">Random Forest scores all {preview.rows.toLocaleString("en-US")} rows</li>
                      <li className={plan(caps?.qsvm) ? "ok" : "skip"}>QSVM {plan(caps?.qsvm) ? "will run" : `skipped (max ${caps?.qsvm ?? "…"} rows)`}</li>
                      <li className={plan(caps?.vqc) ? "ok" : "skip"}>VQC {plan(caps?.vqc) ? "will run" : `skipped (max ${caps?.vqc ?? "…"} rows)`}</li>
                    </ul>
                  )}
                  <div className="drop-actions">
                    <StarButton onClick={run} disabled={busy || preview.missing.length > 0 || preview.rows === 0}>
                      {busy ? "Scoring…" : `Score ${preview.rows.toLocaleString("en-US")} rows →`}
                    </StarButton>
                    <button className="secondary" onClick={reset}>Start over</button>
                  </div>
                  {busy && <p className="muted small" role="status">The quantum models can take several seconds.</p>}
                </>
              )}
            </div>
            {error && (
              <div className="callout bad-callout" role="alert">
                <strong>That didn't work.</strong>
                <p>{error}</p>
                <p className="muted small">Open "Bringing your own CSV?" on the right for the format, or start over with a sample set.</p>
              </div>
            )}
          </Reveal>

          <Reveal delay={0.1}>
            <aside className="guide">
              <h3>How it works</h3>
              <ol className="how">
                <li><strong>Add transactions.</strong> Try a sample set, or bring your own CSV.</li>
                <li><strong>Three models vote.</strong> A classical Random Forest scores every row. Two experimental quantum models join in on small files.</li>
                <li><strong>See who agrees.</strong> Rows where the models disagree are flagged, and you can download everything.</li>
              </ol>
              <details className="fmt">
                <summary>Bringing your own CSV?</summary>
                <p>
                  Each row needs four numbers, named {REQUIRED.join(", ")}. The original card data hides real details like
                  amount and merchant by turning them into anonymous numbers for privacy. These four turned out to be the
                  most useful, so they are all the models see.
                </p>
                <div className="mini-table" role="table" aria-label="Example CSV">
                  <div className="mt-row mt-head" role="row">{REQUIRED.map((c) => <span key={c} role="columnheader">{c}</span>)}</div>
                  {[["-0.25", "0.47", "-0.31", "0.04"], ["-3.57", "-3.64", "-5.54", "-5.14"]].map((r, i) => (
                    <div className="mt-row" role="row" key={i}>{r.map((v, j) => <span key={j} role="cell">{v}</span>)}</div>
                  ))}
                </div>
                <p className="muted small">
                  Extra columns are ignored. Random Forest handles up to {caps ? caps.rf.toLocaleString("en-US") : "50,000"} rows;
                  QSVM up to {caps?.qsvm ?? 25} and VQC up to {caps?.vqc ?? 200}, because they are slower. Values far outside the
                  training range are still scored but flagged.
                </p>
              </details>
            </aside>
          </Reveal>
        </div>

        {result && (
          <motion.section className="results" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ type: "spring", bounce: 0, duration: 0.6 }}>
            <div className="summary">
              <div className="stat"><span className="stat-label">Rows scored</span><span className="stat-value"><CountUp to={result.rows.length} /></span></div>
              <div className="stat"><span className="stat-label">Flagged as fraud by Random Forest</span><span className="stat-value bad"><CountUp to={flagged} /></span></div>
              <div className="stat"><span className="stat-label">Quantum models that ran</span>
                <span className="stat-value">{[result.rows[0]?.qsvm, result.rows[0]?.vqc].filter(Boolean).length} of 2</span></div>
            </div>
            {result.notes.map((n) => <p key={n} className="caveat">{n}</p>)}
            <div className="table-tools">
              <button className={flaggedOnly ? "" : "secondary"} aria-pressed={flaggedOnly} onClick={() => setFlaggedOnly((v) => !v)}>Flagged only</button>
              <button className="secondary" onClick={() => setSort((s) => (s === "risk" ? "row" : "risk"))}>Sorted by {sort === "risk" ? "risk" : "row order"}</button>
              <button className="secondary" onClick={download}>Download results (CSV)</button>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th className="num">Row</th><th>Risk</th><th>Random Forest</th><th>QSVM</th><th>VQC</th><th>Notes</th></tr></thead>
                <tbody>
                  {rows.slice(0, 500).map((r) => (
                    <tr key={r.row}>
                      <td className="num">{r.row}</td>
                      <td><span className="tile-bar wide" aria-hidden="true"><i style={{ width: `${Math.max(2, Math.round(r.rf.score * 100))}%` }} /></span></td>
                      <td><Pill m={r.rf} /></td>
                      <td><Pill m={r.qsvm} /></td>
                      <td><Pill m={r.vqc} /></td>
                      <td className="muted small">{[disagree(r) ? "models disagree" : "", ...r.warnings].filter(Boolean).join(" · ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {rows.length > 500 && <p className="muted small">Showing the first 500 of {rows.length.toLocaleString("en-US")} rows. Download for everything.</p>}
            {flaggedOnly && rows.length === 0 && <p className="muted">Nothing was flagged as fraud in this file.</p>}
          </motion.section>
        )}
      </section>
    </>
  );
}
