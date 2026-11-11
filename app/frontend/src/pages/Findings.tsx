import { useEffect, useMemo, useState } from "react";
import { getFindings } from "../api";
import type { Findings as FindingsData } from "../api";
import BarChart from "../components/BarChart";
import CountUp from "../components/CountUp";
import MetricBars from "../components/MetricBars";
import MetricTable from "../components/MetricTable";
import Reveal from "../components/Reveal";
import Segmented from "../components/Segmented";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";

const MODELS = [
  { value: "Random Forest", label: "Random Forest" },
  { value: "SVM", label: "SVM" },
  { value: "Logistic Regression", label: "Logistic Regression" },
  { value: "VQC", label: "VQC (quantum)" },
];
const BALANCING = [
  { value: "None", label: "No balancing" },
  { value: "SMOTE", label: "SMOTE" },
  { value: "ADASYN", label: "ADASYN" },
];
const BALANCING_TEXT: Record<string, string> = {
  None: "trained on the data exactly as it is",
  SMOTE: "trained with extra synthetic fraud examples (SMOTE)",
  ADASYN: "trained with extra synthetic fraud examples, focused on the hard cases (ADASYN)",
};
const short = (m: string) => (m === "Logistic Regression" ? "LR" : m === "Random Forest" ? "RF" : m);
const money = (n: number) => `${n < 0 ? "−" : "+"}$${Math.abs(Math.round(n)).toLocaleString("en-US")}`;
const num = (v: string | number | undefined) => Number(v ?? 0);

export default function Findings() {
  const status = useServerStatus();
  const [data, setData] = useState<FindingsData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [model, setModel] = useState("Random Forest");
  const [balancing, setBalancing] = useState("None");
  const [mode, setMode] = useState("default");
  const [qBalancing, setQBalancing] = useState("SMOTE");

  useEffect(() => {
    if (status === "ready") getFindings().then(setData).catch((e) => setError(e.message));
  }, [status]);

  const cq = data?.classical_quantum.rows ?? [];
  const cb = data?.cost_benefit.rows ?? [];
  const qv = data?.qsvm_vs_vqc.rows ?? [];

  const row = cq.find((r) => r["Model"] === model && r["Balancing"] === balancing);
  const counts = cb.find((r) => r["Model"] === model && r["Balancing"] === balancing && String(r["Threshold"]).startsWith("Default"));
  const noneCounts = cb.find((r) => r["Model"] === model && r["Balancing"] === "None" && String(r["Threshold"]).startsWith("Default"));

  const headline = useMemo(() => {
    const best = (name: string) => Math.max(...cq.filter((r) => r["Model"] === name).map((r) => num(r["F1 Score"])), 0);
    const bestNet = (name: string) => Math.max(...cb.filter((r) => r["Model"] === name).map((r) => num(r["Net Benefit ($)"])), -Infinity);
    return { rfF1: best("Random Forest"), vqcF1: best("VQC"), rfNet: bestNet("Random Forest"), vqcNet: bestNet("VQC") };
  }, [cq, cb]);

  const modeRows = cb.filter((r) => (mode === "default" ? String(r["Threshold"]).startsWith("Default") : r["Threshold"] === "Best-F1"));
  const costBars = ["Random Forest", "SVM", "Logistic Regression", "VQC"].map((m) => ({
    label: short(m),
    value: Math.max(...modeRows.filter((r) => r["Model"] === m).map((r) => num(r["Net Benefit ($)"]))),
  }));
  const losing = modeRows.filter((r) => num(r["Net Benefit ($)"]) < 0).length;

  const qsvm = qv.find((r) => r["Model"] === "QSVM" && r["Balancing"] === qBalancing);
  const vqcM = qv.find((r) => String(r["Model"]).startsWith("VQC") && r["Balancing"] === qBalancing);
  const pair = (r: typeof qsvm) => [
    { label: "F1", hint: "Balance of precision and recall", value: num(r?.["F1 Score"]) },
    { label: "Precision", hint: "When it says fraud, how often it's right", value: num(r?.["Precision"]) },
    { label: "Recall", hint: "Share of real fraud it catches", value: num(r?.["Recall"]) },
  ];

  return (
    <>
      <ServerBanner state={status} />
      <section className="page">
        <h1>Findings</h1>
        <p className="lede small-lede">
          Does quantum machine learning catch fraud better than classical? Short answer: not yet. Here is the evidence,
          and you can poke at it. Every number comes straight from the paper's results files.
        </p>
        {error && <p className="bad" role="alert">{error}</p>}

        {data && (
          <>
            <Reveal className="verdict-band">
              <div className="stat">
                <span className="stat-label">Best F1 score, classical</span>
                <span className="stat-value good">{headline.rfF1.toFixed(2)}</span>
                <span className="muted small">Random Forest</span>
              </div>
              <div className="stat">
                <span className="stat-label">Best F1 score, quantum VQC</span>
                <span className="stat-value bad">{headline.vqcF1.toFixed(2)}</span>
                <span className="muted small">Close to useless on the real, imbalanced test set</span>
              </div>
              <div className="stat">
                <span className="stat-label">Best net benefit, Random Forest</span>
                <span className="stat-value good"><CountUp to={Math.abs(headline.rfNet)} prefix="+$" /></span>
                <span className="muted small">
                  Quantum VQC's best:{" "}
                  <strong className="bad"><CountUp to={Math.abs(headline.vqcNet)} prefix={headline.vqcNet < 0 ? "−$" : "+$"} /></strong>
                </span>
              </div>
            </Reveal>

            <Reveal>
              <h2 className="section-title">1 · How well does each model catch fraud?</h2>
              <p className="muted">Pick a model and how it was trained. The bars move; the explanation underneath follows.</p>
              <div className="controls">
                <Segmented label="Model" options={MODELS} value={model} onChange={setModel} />
                <Segmented label="Training" options={BALANCING} value={balancing} onChange={setBalancing} />
              </div>
              <div className="panel">
                {row && (
                  <MetricBars items={[
                    { label: "Precision", hint: "When it cries fraud, how often it is right.", value: num(row["Precision"]) },
                    { label: "Recall", hint: "Of all real frauds, how many it caught.", value: num(row["Recall"]) },
                    { label: "F1 score", hint: "One score that balances precision and recall.", value: num(row["F1 Score"]) },
                    { label: "ROC AUC", hint: "How well it ranks fraud above legitimate, whatever the cut-off.", value: num(row["ROC AUC"]) },
                  ]} />
                )}
                {counts && (
                  <p className="story">
                    {MODELS.find((m) => m.value === model)?.label}, {BALANCING_TEXT[balancing]}: out of{" "}
                    <strong>{num(counts["TP"]) + num(counts["FN"])}</strong> real frauds it caught <strong className="good">{num(counts["TP"])}</strong> and
                    missed <strong className="bad">{num(counts["FN"])}</strong>. It also raised <strong>{num(counts["FP"]).toLocaleString("en-US")}</strong> false
                    alarms on {(num(counts["FP"]) + num(counts["TN"])).toLocaleString("en-US")} legitimate transactions.
                    {balancing !== "None" && noneCounts && num(counts["FP"]) > num(noneCounts["FP"]) * 3 && (
                      <> Without balancing it raised only <strong>{num(noneCounts["FP"]).toLocaleString("en-US")}</strong>: more fraud caught, but at the price of far more false alarms for analysts to review.</>
                    )}
                  </p>
                )}
                <p className="muted small">Accuracy is left out on purpose: with 0.17% fraud, a model that flags nothing scores about 99.8%.</p>
              </div>
            </Reveal>

            <Reveal>
              <h2 className="section-title">2 · What does it cost?</h2>
              <p className="muted">Net benefit is the fraud value a model catches minus what it costs analysts to investigate its alerts. Switch the cut-off to see why it matters.</p>
              <div className="controls">
                <Segmented label="Cut-off" options={[{ value: "default", label: "Default (0.5)" }, { value: "tuned", label: "Tuned for best F1" }]} value={mode} onChange={setMode} />
              </div>
              <div className="panel">
                <p className="muted small">Best result for each model across its training options:</p>
                <BarChart key={mode} bars={costBars} />
                <p className="story">
                  {mode === "default"
                    ? <>At the default cut-off, <strong className="bad">{losing} of {modeRows.length}</strong> settings lose money. Balancing the training data teaches models to cry wolf, and every false alarm costs an investigation.</>
                    : <>Tuning the cut-off rescues the classical models, but the best quantum VQC setting still ends at <strong className="bad">{money(headline.vqcNet)}</strong>.</>}
                </p>
                {mode === "tuned" && <p className="caveat">{data.cost_benefit.caveat}</p>}
              </div>
            </Reveal>

            <Reveal>
              <h2 className="section-title">3 · Quantum against quantum</h2>
              <p className="muted">The quantum kernel method (QSVM) beats the variational one (VQC) head to head. This comparison only exists on a small, matched subset of the data.</p>
              <div className="controls">
                <Segmented label="Training" options={BALANCING} value={qBalancing} onChange={setQBalancing} />
              </div>
              <div className="panel two">
                <div><h3>QSVM</h3><MetricBars items={pair(qsvm)} /></div>
                <div><h3>VQC</h3><MetricBars items={pair(vqcM)} /></div>
              </div>
              <p className="caveat">{data.qsvm_vs_vqc.caveat}</p>
            </Reveal>

            <Reveal>
              <h2 className="section-title">4 · Read this before quoting a number</h2>
              <div className="caveats">
                <div className="note"><strong>Real fraud is rare.</strong><p>About 0.17% of transactions. That is why accuracy is misleading and why precision and recall matter.</p></div>
                <div className="note"><strong>Simulator, not hardware.</strong><p>The quantum models ran on a classical computer simulating a quantum one. Real hardware adds noise.</p></div>
                <div className="note"><strong>Tuned cut-offs are optimistic.</strong><p>The "best F1" thresholds were picked using the test labels, so treat those results as an upper bound.</p></div>
                <div className="note"><strong>One test set.</strong><p>Results come from a single split. The multi-seed runs show VQC varies a lot from run to run.</p></div>
              </div>
            </Reveal>

            <Reveal>
              <details className="raw">
                <summary>Show the raw tables</summary>
                <h3>Full test set: all models</h3>
                <MetricTable table={data.classical_quantum} columns={["Model", "Balancing", "Precision", "Recall", "F1 Score", "ROC AUC", "Accuracy"]} mutedColumns={["Accuracy"]} />
                <h3>Cost of every setting</h3>
                <MetricTable table={data.cost_benefit} columns={["Model", "Balancing", "Threshold", "TP", "FP", "FN", "TN", "Net Benefit ($)"]} />
                <h3>Threshold tuning</h3>
                <MetricTable table={data.thresholds} columns={["Model", "Balancing", "Default F1", "Best-F1 Threshold", "Best-F1 F1"]} />
              </details>
            </Reveal>
          </>
        )}
      </section>
    </>
  );
}
