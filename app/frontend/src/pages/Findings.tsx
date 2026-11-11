import { useEffect, useState } from "react";
import { getFindings } from "../api";
import type { Findings as FindingsData } from "../api";
import { ServerBanner, useServerStatus } from "../components/ServerStatus";
import MetricTable from "../components/MetricTable";

export default function Findings() {
  const status = useServerStatus();
  const [data, setData] = useState<FindingsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "ready") getFindings().then(setData).catch((e) => setError(e.message));
  }, [status]);

  const vqc = data?.cost_benefit.rows.filter((r) => r["Model"] === "VQC") ?? [];
  const allVqcNegative = vqc.length > 0 && vqc.every((r) => Number(r["Net Benefit ($)"]) < 0);
  const classical = data
    ? { ...data.classical_quantum, rows: [...data.classical_quantum.rows].sort((a, b) => Number(b["F1 Score"]) - Number(a["F1 Score"])) }
    : null;

  return (
    <>
      <ServerBanner state={status} />
      <section className="page">
        <h1>Findings</h1>
        <p className="lede small-lede">Every figure below is read from the paper's results files, not retyped.</p>
        {error && <p className="bad" role="alert">{error}</p>}
        {data && classical && (
          <>
            <h3>Precision, recall and F1 on the full test set</h3>
            <p className="muted small">
              Accuracy is shown last and muted on purpose: only about 0.17% of transactions are fraud, so a model
              that flags nothing scores about 99.8% accuracy while catching no fraud.
            </p>
            <MetricTable table={classical}
              columns={["Model", "Balancing", "Precision", "Recall", "F1 Score", "ROC AUC", "Accuracy"]}
              mutedColumns={["Accuracy"]} />

            <h3>What it costs: net benefit</h3>
            <p className="muted small">Net benefit = fraud value caught minus investigation cost.</p>
            {allVqcNegative && <p className="caveat">Every VQC setting in this table loses money.</p>}
            <MetricTable table={data.cost_benefit}
              columns={["Model", "Balancing", "Threshold", "TP", "FP", "FN", "TN", "Net Benefit ($)"]} />

            <h3>QSVM vs VQC on the matched subset</h3>
            <MetricTable table={data.qsvm_vs_vqc}
              columns={["Model", "Balancing", "Precision", "Recall", "F1 Score", "ROC AUC", "Accuracy"]}
              mutedColumns={["Accuracy"]} />

            <h3>Threshold tuning</h3>
            <MetricTable table={data.thresholds}
              columns={["Model", "Balancing", "Default F1", "Best-F1 Threshold", "Best-F1 Precision", "Best-F1 Recall", "Best-F1 F1"]} />
          </>
        )}
      </section>
    </>
  );
}
