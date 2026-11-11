import { useEffect, useState } from "react";
import { getMeta, getSamples, scoreCsv } from "../api";
import type { Meta, ModelScore, ScoreResult } from "../api";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";

const cell = (m: ModelScore | null) =>
  m ? `${m.label === 1 ? "Fraud" : "Legit"} (${(m.score * 100).toFixed(1)}%)` : "—";

export default function Upload() {
  const status = useServerStatus();
  const [meta, setMeta] = useState<Meta | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScoreResult | null>(null);

  useEffect(() => {
    if (status === "ready") getMeta().then(setMeta).catch(() => setMeta(null));
  }, [status]);

  const onFile = async (file: File | undefined) => {
    if (!file) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await scoreCsv(file));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const downloadExample = async () => {
    const rows = (await getSamples()).slice(0, 3);
    const csv = ["V10,V12,V14,V17", ...rows.map((s) => Object.values(s.features).join(","))].join("\n") + "\n";
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = "example.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const caps = meta?.caps;
  return (
    <>
      <ServerBanner state={status} />
      <section className="page">
        <h1>Upload a CSV</h1>
        <p className="lede small-lede">
          Required columns: <code>V10, V12, V14, V17</code> (numbers only; other columns are ignored).
          {caps && ` Up to ${caps.rf.toLocaleString("en-US")} rows for Random Forest; the experimental quantum models
          run on at most ${caps.qsvm} rows (QSVM) and ${caps.vqc} rows (VQC).`} Files are scored and discarded, never stored.
        </p>
        <p>
          <input type="file" accept=".csv,text/csv" disabled={status !== "ready" || busy}
                 onChange={(e) => onFile(e.target.files?.[0])} aria-label="Choose a CSV file" />{" "}
          <button className="secondary" onClick={downloadExample} disabled={status !== "ready"}>Download an example CSV</button>
        </p>
        {busy && <p role="status">Scoring… the quantum models can take several seconds.</p>}
        {error && <p className="bad" role="alert">{error}</p>}
        {result && (
          <>
            {result.notes.map((n) => <p key={n} className="caveat">{n}</p>)}
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th className="num">Row</th><th>Random Forest</th><th>QSVM (experimental)</th><th>VQC (experimental)</th><th>Flags</th></tr>
                </thead>
                <tbody>
                  {result.rows.slice(0, 1000).map((r) => (
                    <tr key={r.row}>
                      <td className="num">{r.row}</td>
                      <td className={r.rf.label === 1 ? "bad" : ""}>{cell(r.rf)}</td>
                      <td>{cell(r.qsvm)}</td>
                      <td>{cell(r.vqc)}</td>
                      <td className="muted">{r.warnings.join("; ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {result.rows.length > 1000 && <p className="muted small">Showing the first 1,000 of {result.rows.length.toLocaleString("en-US")} rows.</p>}
          </>
        )}
      </section>
    </>
  );
}
