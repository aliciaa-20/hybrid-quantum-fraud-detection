import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFindings, getSamples } from "../api";
import type { Findings, Sample } from "../api";
import CountUp from "../components/CountUp";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";
import Ticker from "../components/Ticker";
import VerdictCollapse from "../components/VerdictCollapse";
import WordReveal from "../components/WordReveal";

function bestNet(f: Findings, model: string): number {
  return Math.max(...f.cost_benefit.rows.filter((r) => r["Model"] === model).map((r) => Number(r["Net Benefit ($)"])));
}

export default function Landing() {
  const status = useServerStatus();
  const [samples, setSamples] = useState<Sample[]>([]);
  const [findings, setFindings] = useState<Findings | null>(null);
  const [picked, setPicked] = useState<{ sample: Sample; run: number } | null>(null);

  useEffect(() => {
    if (status !== "ready") return;
    getSamples().then(setSamples).catch(() => setSamples([]));
    getFindings().then(setFindings).catch(() => setFindings(null));
  }, [status]);

  const ready = status === "ready" && samples.length > 0;

  const score = () => {
    if (!ready) return;
    // Half the time pick a known fraud so the demo is not a wall of "legit".
    const pool = samples.filter((s) => s.actual === (Math.random() < 0.5 ? 1 : 0));
    const sample = pool[Math.floor(Math.random() * pool.length)];
    setPicked((p) => ({ sample, run: (p?.run ?? 0) + 1 }));
  };

  const rf = findings ? bestNet(findings, "Random Forest") : null;
  const vqc = findings ? bestNet(findings, "VQC") : null;

  const entries = [
    { to: "/explore", title: "Browse transactions", text: "Real test-set transactions, scored by three models side by side." },
    { to: "/upload", title: "Upload a CSV", text: "Score your own small file. Nothing is stored." },
    { to: "/findings", title: "Read the findings", text: "Precision, recall and cost, with every caveat attached." },
  ];

  return (
    <>
      <ServerBanner state={status} />
      <section className="hero2">
        <div className="giant" aria-hidden="true">NICE TRY</div>
        <div className="hero-in">
          <p className="eyebrow">Hybrid quantum fraud detection</p>
          <h1>
            <WordReveal text="Fraudsters," />
            <WordReveal text="nice try." className="grad" delay={0.25} />
          </h1>
          <p className="lede">
            Classical vs quantum, head to head on real credit card transactions. Spoiler: classical is winning.
          </p>

          <div className="cmd">
            <span>{ready ? "Pull a real transaction and let the model decide…" : "Waking the models…"}</span>
            <button className="go" onClick={score} disabled={!ready}>Score it →</button>
          </div>

          <AnimatePresence mode="wait">
            {picked && (
              <motion.div
                key={picked.run}
                className="result"
                initial={{ opacity: 0, y: 16, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}
              >
                <div className="result-head">
                  <strong>Random Forest · #{picked.sample.test_index}</strong>
                  <span className="muted small">random demo transaction</span>
                </div>
                <VerdictCollapse label={picked.sample.rf.label} score={picked.sample.rf.score} run={picked.run} big />
                <RevealTruth sample={picked.sample} run={picked.run} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="orb-wrap" aria-hidden="true">
          <div className="ring r1" /><div className="ring r2" /><div className="ring r3" />
          <div className="orb" />
        </div>
        <Ticker samples={samples} />
      </section>

      <section className="entries" aria-label="Where to start">
        {entries.map((e, i) =>
          status === "ready" ? (
            <motion.div key={e.to} initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.5 }}>
              <Link to={e.to} className="entry">
                <h2>{e.title}</h2>
                <p>{e.text}</p>
                <span className="arrow">→</span>
              </Link>
            </motion.div>
          ) : (
            <div key={e.to} className="entry disabled" aria-disabled="true">
              <h2>{e.title}</h2>
              <p>{e.text}</p>
            </div>
          ),
        )}
      </section>

      <section className="stats" aria-label="Headline result">
        <div>
          <span className="stat-label">Random Forest, best net benefit</span>
          <span className="stat-value good">{rf === null ? "…" : <CountUp to={Math.abs(rf)} prefix={rf < 0 ? "−$" : "+$"} />}</span>
        </div>
        <div>
          <span className="stat-label">Quantum VQC, best net benefit in any setting</span>
          <span className="stat-value bad">{vqc === null ? "…" : <CountUp to={Math.abs(vqc)} prefix={vqc < 0 ? "−$" : "+$"} />}</span>
        </div>
        <p className="stat-note">
          Net benefit is fraud value caught minus investigation cost, on the full test set. See Findings for the
          definition and caveats.
        </p>
      </section>
    </>
  );
}

/** After the verdict collapses, say honestly whether the model was right. */
function RevealTruth({ sample, run }: { sample: Sample; run: number }) {
  const [show, setShow] = useState(false);
  useEffect(() => {
    setShow(false);
    const t = window.setTimeout(() => setShow(true), 1100);
    return () => window.clearTimeout(t);
  }, [run]);
  const right = sample.rf.label === sample.actual;
  return (
    <div className="truth" style={{ minHeight: "1.6em" }}>
      {show && (
        <motion.span initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className={right ? "good" : "bad"}>
          True label: {sample.actual === 1 ? "fraud" : "legitimate"}.{" "}
          {right ? "The model got it right." : sample.actual === 1 ? "The model missed it." : "A false alarm."}
        </motion.span>
      )}
    </div>
  );
}
