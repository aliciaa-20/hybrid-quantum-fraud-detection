import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getFindings } from "../api";
import type { Findings } from "../api";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";

const money = (n: number) =>
  `${n < 0 ? "−" : "+"}$${Math.abs(Math.round(n)).toLocaleString("en-US")}`;

function netBenefits(f: Findings, model: string): number[] {
  return f.cost_benefit.rows
    .filter((r) => r["Model"] === model)
    .map((r) => Number(r["Net Benefit ($)"]));
}

export default function Landing() {
  const status = useServerStatus();
  const [findings, setFindings] = useState<Findings | null>(null);

  useEffect(() => {
    if (status === "ready") getFindings().then(setFindings).catch(() => setFindings(null));
  }, [status]);

  const ready = status === "ready";
  const rf = findings ? Math.max(...netBenefits(findings, "Random Forest")) : null;
  const vqc = findings ? Math.max(...netBenefits(findings, "VQC")) : null;

  const entries = [
    { to: "/explore", title: "Try a sample transaction", text: "Browse real test-set transactions and see how each model scores them." },
    { to: "/upload", title: "Upload a CSV", text: "Score your own small file of transactions." },
    { to: "/findings", title: "Read the findings", text: "Precision, recall, cost and caveats, straight from the paper's results." },
  ];

  return (
    <>
      <ServerBanner state={status} />
      <section className="hero">
        <p className="eyebrow">Honors project · Hybrid quantum machine learning</p>
        <h1>Does quantum beat classical at catching fraud?</h1>
        <p className="lede">Honest answer: not yet. This site lets you see why, on real transactions.</p>
      </section>

      <section className="entries" aria-label="Where to start">
        {entries.map((e) =>
          ready ? (
            <Link key={e.to} to={e.to} className="entry">
              <h2>{e.title}</h2>
              <p>{e.text}</p>
            </Link>
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
          <span className="stat-value">{rf === null ? "…" : money(rf)}</span>
        </div>
        <div>
          <span className="stat-label">Quantum VQC, best net benefit in any setting</span>
          <span className="stat-value">{vqc === null ? "…" : money(vqc)}</span>
        </div>
        <p className="stat-note">
          Net benefit is fraud value caught minus investigation cost, on the full test set. See Findings for the
          definition and caveats.
        </p>
      </section>
    </>
  );
}
