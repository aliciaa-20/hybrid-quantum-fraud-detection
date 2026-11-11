import type { ModelScore } from "../api";
import VerdictCollapse from "./VerdictCollapse";

type Props = {
  model: string;
  result: ModelScore;
  actual?: 0 | 1;
  experimental?: boolean;
  caption?: string;
  run?: number | string;
  delay?: number;
};

export function outcome(label: 0 | 1, actual: 0 | 1): { text: string; ok: boolean } {
  if (label === actual) return { text: "Correct", ok: true };
  return actual === 1 ? { text: "Missed fraud", ok: false } : { text: "False alarm", ok: false };
}

export default function ScoreCard({ model, result, actual, experimental, caption, run = 0, delay = 0 }: Props) {
  const o = actual === undefined ? null : outcome(result.label, actual);
  return (
    <div className="score-card">
      <div className="score-head">
        <strong>{model}</strong>
        {experimental && <span className="tag">experimental</span>}
        <span className="tag muted-tag">{result.source}</span>
      </div>
      <VerdictCollapse label={result.label} score={result.score} run={run} delay={delay} />
      {o && <div className={`outcome ${o.ok ? "good" : "bad"}`}>{o.text}</div>}
      {caption && <div className="muted small">{caption}</div>}
    </div>
  );
}
