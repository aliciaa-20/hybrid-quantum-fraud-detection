import type { ModelScore } from "../api";

type Props = {
  model: string;
  result: ModelScore;
  actual?: 0 | 1;
  experimental?: boolean;
  caption?: string;
};

export function outcome(label: 0 | 1, actual: 0 | 1): { text: string; ok: boolean } {
  if (label === actual) return { text: "Correct", ok: true };
  return actual === 1 ? { text: "Missed fraud", ok: false } : { text: "False alarm", ok: false };
}

export default function ScoreCard({ model, result, actual, experimental, caption }: Props) {
  const verdict = result.label === 1 ? "Fraud" : "Legitimate";
  const o = actual === undefined ? null : outcome(result.label, actual);
  return (
    <div className="score-card">
      <div className="score-head">
        <strong>{model}</strong>
        {experimental && <span className="tag">experimental</span>}
        <span className="tag muted-tag">{result.source}</span>
      </div>
      <div className={`verdict ${result.label === 1 ? "bad" : "good"}`}>{verdict}</div>
      <div className="muted">Fraud probability {(result.score * 100).toFixed(1)}%</div>
      {o && <div className={o.ok ? "good" : "bad"}>{o.text}</div>}
      {caption && <div className="muted small">{caption}</div>}
    </div>
  );
}
