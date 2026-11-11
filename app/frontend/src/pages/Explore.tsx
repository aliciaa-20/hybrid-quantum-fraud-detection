import { useEffect, useMemo, useState } from "react";
import { getSamples, liveScore } from "../api";
import type { LiveResult, Sample } from "../api";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";
import ScoreCard from "../components/ScoreCard";

type Filter = "all" | "fraud" | "legit";

export default function Explore() {
  const status = useServerStatus();
  const [samples, setSamples] = useState<Sample[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("fraud");
  const [selected, setSelected] = useState<Sample | null>(null);
  const [live, setLive] = useState<LiveResult | null>(null);
  const [liveBusy, setLiveBusy] = useState(false);
  const [liveError, setLiveError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "ready") getSamples().then(setSamples).catch((e) => setError(e.message));
  }, [status]);

  const shown = useMemo(
    () => samples.filter((s) => filter === "all" || (filter === "fraud" ? s.actual === 1 : s.actual === 0)),
    [samples, filter],
  );
  const frauds = samples.filter((s) => s.actual === 1).length;

  const pick = (s: Sample) => {
    setSelected(s);
    setLive(null);
    setLiveError(null);
  };

  const runLive = async () => {
    if (!selected) return;
    setLiveBusy(true);
    setLiveError(null);
    try {
      setLive(await liveScore(selected.id));
    } catch (e) {
      setLiveError((e as Error).message + " The stored scores above are still valid.");
    } finally {
      setLiveBusy(false);
    }
  };

  return (
    <>
      <ServerBanner state={status} />
      <section className="page">
        <h1>Explore sample transactions</h1>
        <p className="lede small-lede">
          {samples.length > 0 ? `${samples.length} real test-set transactions, ${frauds} of them known fraud. ` : ""}
          This set is deliberately class-enriched (about 38% fraud; the real rate is about 0.17%), so do not read
          accuracy off it. Misses and false alarms are shown, not hidden.
        </p>
        {error && <p className="bad" role="alert">{error}</p>}

        <div className="filters" role="group" aria-label="Filter transactions">
          {(["fraud", "legit", "all"] as Filter[]).map((f) => (
            <button key={f} className={filter === f ? "" : "secondary"} onClick={() => setFilter(f)}>
              {f === "fraud" ? "Known fraud" : f === "legit" ? "Legitimate" : "All"}
            </button>
          ))}
        </div>

        <div className="explore">
          <ul className="sample-list" aria-label="Transactions">
            {shown.map((s) => (
              <li key={s.id}>
                <button className={`sample-item ${selected?.id === s.id ? "on" : ""}`} onClick={() => pick(s)}>
                  <span>#{s.test_index}</span>
                  <span className={s.actual === 1 ? "bad" : "muted"}>{s.actual === 1 ? "fraud" : "legit"}</span>
                  <span className="muted">RF {(s.rf.score * 100).toFixed(0)}%</span>
                </button>
              </li>
            ))}
          </ul>

          <div className="detail">
            {!selected ? (
              <p className="muted">Pick a transaction to see how each model scored it.</p>
            ) : (
              <>
                <h2>Transaction #{selected.test_index}</h2>
                <p>
                  True label: <strong className={selected.actual === 1 ? "bad" : "good"}>
                    {selected.actual === 1 ? "Fraud" : "Legitimate"}</strong>
                </p>
                <p className="muted small">
                  {Object.entries(selected.features).map(([k, v]) => `${k} = ${v.toFixed(3)}`).join(" · ")}
                  {" "}(anonymized components from the public ULB dataset)
                </p>
                <div className="cards3">
                  <ScoreCard model="Random Forest" result={selected.rf} actual={selected.actual} />
                  <ScoreCard model="QSVM" result={selected.qsvm} actual={selected.actual} experimental
                             caption="Matched-subset model, simulator" />
                  <ScoreCard model="VQC (paper run)" result={selected.vqc_paper} actual={selected.actual} experimental
                             caption="Stored output from the paper's run" />
                </div>

                <button onClick={runLive} disabled={liveBusy}>
                  {liveBusy ? "Running on the simulator…" : "Run quantum models live"}
                </button>
                {liveError && <p className="bad" role="alert">{liveError}</p>}
                {live && (
                  <div className="live">
                    <div className="cards3">
                      <ScoreCard model="QSVM (live)" result={live.qsvm} actual={selected.actual} experimental />
                      <ScoreCard model="VQC (live re-run)" result={live.vqc_live} actual={selected.actual} experimental />
                    </div>
                    {live.notes.map((n) => <p key={n} className="caveat">{n}</p>)}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
