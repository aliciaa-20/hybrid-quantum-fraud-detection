import { useEffect, useMemo, useRef, useState } from "react";
import { getSamples, liveScore } from "../api";
import type { LiveResult, Sample } from "../api";
import Reveal from "../components/Reveal";
import StarButton from "../components/StarButton";
import ScoreCard from "../components/ScoreCard";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";

type Filter = "all" | "fraud" | "legit";
const txn = (n: number) => n.toLocaleString("en-US");

export default function Explore() {
  const status = useServerStatus();
  const [samples, setSamples] = useState<Sample[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("fraud");
  const [selected, setSelected] = useState<Sample | null>(null);
  const [live, setLive] = useState<LiveResult | null>(null);
  const [liveBusy, setLiveBusy] = useState(false);
  const [liveError, setLiveError] = useState<string | null>(null);
  const featured = useRef<HTMLElement>(null);

  useEffect(() => {
    if (status !== "ready") return;
    getSamples()
      .then((s) => {
        setSamples(s);
        setSelected((cur) => cur ?? s.find((x) => x.actual === 1 && x.rf.label === 1) ?? s.find((x) => x.actual === 1) ?? s[0] ?? null); // never an empty state; misses are in the grid
      })
      .catch((e) => setError(e.message));
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
    featured.current?.scrollIntoView({ behavior: "smooth", block: "start" });
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
        <h1>Explore</h1>
        <p className="lede small-lede">
          {samples.length > 0 ? `${samples.length} real test-set transactions, ${frauds} of them known fraud. ` : ""}
          This set is deliberately class-enriched (about 38% fraud; the real rate is about 0.17%), so do not read
          accuracy off it. Misses and false alarms are shown, not hidden.
        </p>
        {error && <p className="bad" role="alert">{error}</p>}

        {selected && (
          <section className="featured" ref={featured} aria-label="Selected transaction">
            <div className="featured-head">
              <div>
                <p className="eyebrow">Selected transaction</p>
                <h2 className="big-num">Txn {txn(selected.test_index)}</h2>
              </div>
              <div className={`truth-chip ${selected.actual === 1 ? "f" : "l"}`}>
                True label: {selected.actual === 1 ? "Fraud" : "Legitimate"}
              </div>
            </div>
            <p className="features">
              {Object.entries(selected.features).map(([k, v]) => (
                <span key={k} className="feat"><em>{k}</em> {v.toFixed(2)}</span>
              ))}
              <span className="muted small">anonymized PCA components from the public ULB dataset</span>
            </p>
            <div className="cards3">
              <ScoreCard model="Random Forest" result={selected.rf} actual={selected.actual} run={selected.id} />
              <ScoreCard model="QSVM" result={selected.qsvm} actual={selected.actual} experimental
                         caption="Matched-subset model, simulator" run={selected.id} delay={300} />
              <ScoreCard model="VQC (paper run)" result={selected.vqc_paper} actual={selected.actual} experimental
                         caption="Stored output from the paper's run" run={selected.id} delay={600} />
            </div>
            <div className="live-row">
              <StarButton onClick={runLive} disabled={liveBusy}>{liveBusy ? "Running on the simulator…" : "Run quantum models live"}</StarButton>
              <span className="muted small">Re-scores this transaction on the simulator; about a second.</span>
            </div>
            {liveError && <p className="bad" role="alert">{liveError}</p>}
            {live && (
              <div className="live">
                <div className="cards3">
                  <ScoreCard model="QSVM (live)" result={live.qsvm} actual={selected.actual} experimental run={`live-${selected.id}`} />
                  <ScoreCard model="VQC (live re-run)" result={live.vqc_live} actual={selected.actual} experimental run={`live-${selected.id}`} delay={300} />
                </div>
                {live.notes.map((n) => <p key={n} className="caveat">{n}</p>)}
              </div>
            )}
          </section>
        )}

        <Reveal>
          <div className="grid-head">
            <h3>Pick another transaction</h3>
            <div className="filters" role="group" aria-label="Filter transactions">
              {(["fraud", "legit", "all"] as Filter[]).map((f) => (
                <button key={f} className={filter === f ? "" : "secondary"} onClick={() => setFilter(f)} aria-pressed={filter === f}>
                  {f === "fraud" ? "Known fraud" : f === "legit" ? "Legitimate" : "All"}
                </button>
              ))}
            </div>
          </div>
        </Reveal>
        <div className="tiles">
          {shown.map((s) => {
            const risk = Math.round(s.rf.score * 100);
            return (
              <button key={s.id} className={`tile ${selected?.id === s.id ? "on" : ""}`} onClick={() => pick(s)} aria-pressed={selected?.id === s.id}>
                <span className="tile-top">
                  <span className="tile-num">Txn {txn(s.test_index)}</span>
                  <span className={`pill ${s.actual === 1 ? "f" : "l"}`}>{s.actual === 1 ? "Fraud" : "Legit"}</span>
                </span>
                <span className="tile-bar" aria-hidden="true"><i style={{ width: `${Math.max(2, risk)}%` }} /></span>
                <span className="tile-risk">Random Forest risk {risk}%</span>
              </button>
            );
          })}
        </div>
      </section>
    </>
  );
}
