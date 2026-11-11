import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFindings, getSamples } from "../api";
import type { Findings, Sample } from "../api";
import CountUp from "../components/CountUp";
import Reveal from "../components/Reveal";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";
import Ticker from "../components/Ticker";
import VerdictCollapse from "../components/VerdictCollapse";
import StarButton from "../components/StarButton";
import TextPressure from "../components/TextPressure";

const cbRows = (f: Findings, model: string) => f.cost_benefit.rows.filter((r) => r["Model"] === model);
const bestNet = (f: Findings, model: string) => Math.max(...cbRows(f, model).map((r) => Number(r["Net Benefit ($)"])));
const txn = (n: number) => n.toLocaleString("en-US");

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
  // Random Forest with no balancing at the default 0.5 threshold: the configuration the app serves.
  const rfDefault = findings?.cost_benefit.rows.find(
    (r) => r["Model"] === "Random Forest" && r["Balancing"] === "None" && String(r["Threshold"]).startsWith("Default"),
  );
  const caught = rfDefault ? Number(rfDefault["TP"]) : null;
  const totalFraud = rfDefault ? Number(rfDefault["TP"]) + Number(rfDefault["FN"]) : null;

  const entries = [
    { to: "/explore", title: "Browse transactions", text: "Real test-set transactions, scored by three models side by side." },
    { to: "/upload", title: "Upload a CSV", text: "Score your own small file. Nothing is stored." },
    { to: "/findings", title: "Read the findings", text: "Precision, recall and cost, with every caveat attached." },
  ];

  return (
    <>
      <ServerBanner state={status} />
      <section className="hero2">
        <div className="hero-in">
          <p className="eyebrow">Hybrid quantum fraud detection</p>
          <motion.h1
            aria-label="Fraudsters, nice try."
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", bounce: 0, duration: 0.8 }}
          >
            <TextPressure segments={[{ text: "Fraudsters," }, { text: "nice try.", gradient: ["#ffc26b", "#ff7a59"] }]} />
          </motion.h1>
          <p className="lede">
            Classical vs quantum, head to head on real credit card transactions. Spoiler: classical is winning.
          </p>

          <div className="cmd">
            <span>{ready ? "Pull a real transaction and let the model decide…" : "Waking the models…"}</span>
            <StarButton onClick={score} disabled={!ready}>Score it →</StarButton>
          </div>

          <motion.div className="result-slot" initial={false} animate={{ height: picked ? "auto" : 0 }} transition={{ type: "spring", bounce: 0, duration: 0.55 }}>
            <AnimatePresence mode="wait">
              {picked && (
                <motion.div
                  key={picked.run}
                  className="result"
                  initial={{ opacity: 0, y: 16, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1, transition: { type: "spring", bounce: 0, duration: 0.45 } }}
                  exit={{ opacity: 0, transition: { duration: 0.1 } }}
                >
                  <div className="result-head">
                    <strong>Random Forest · Txn {txn(picked.sample.test_index)}</strong>
                    <span className="muted small">random demo transaction</span>
                  </div>
                  <VerdictCollapse label={picked.sample.rf.label} score={picked.sample.rf.score} run={picked.run} big />
                  <RevealTruth sample={picked.sample} run={picked.run} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

        <div className="stage" aria-hidden="true">
          <div className="giant">NICE TRY</div>
          <div className="orb" />
          <Ticker samples={samples} />
        </div>
      </section>

      <section className="entries" aria-label="Where to start">
        {entries.map((e, i) =>
          status === "ready" ? (
            <Reveal key={e.to} delay={i * 0.08}>
              <Link to={e.to} className="entry">
                <h2>{e.title}</h2>
                <p>{e.text}</p>
                <span className="arrow">→</span>
              </Link>
            </Reveal>
          ) : (
            <div key={e.to} className="entry disabled" aria-disabled="true">
              <h2>{e.title}</h2>
              <p>{e.text}</p>
            </div>
          ),
        )}
      </section>

      <section className="stats" aria-label="Headline result">
        <Reveal className="stat">
          <span className="stat-label">Random Forest, frauds caught at default settings</span>
          <span className="stat-value">
            {caught === null || totalFraud === null ? "…" : <><CountUp to={caught} /> of {totalFraud}</>}
          </span>
        </Reveal>
        <Reveal className="stat" delay={0.08}>
          <span className="stat-label">Random Forest, best net benefit</span>
          <span className="stat-value good">{rf === null ? "…" : <CountUp to={Math.abs(rf)} prefix={rf < 0 ? "−$" : "+$"} />}</span>
        </Reveal>
        <Reveal className="stat" delay={0.16}>
          <span className="stat-label">Quantum VQC, best net benefit in any setting</span>
          <span className="stat-value bad">{vqc === null ? "…" : <CountUp to={Math.abs(vqc)} prefix={vqc < 0 ? "−$" : "+$"} />}</span>
        </Reveal>
      </section>
      <Reveal>
        <p className="stat-note">
          Net benefit is fraud value caught minus investigation cost, on the full test set. See Findings for the
          definition and caveats.
        </p>
      </Reveal>
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
