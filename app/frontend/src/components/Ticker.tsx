import type { Sample } from "../api";

/** Endless strip of real sample transactions with the Random Forest's call on each. Pauses on hover. */
export default function Ticker({ samples }: { samples: Sample[] }) {
  if (samples.length === 0) return null;
  // Interleave known frauds and legitimate rows so the strip is not a wall of "legit". Colour is the model's call.
  const frauds = samples.filter((s) => s.actual === 1).slice(0, 12);
  const legit = samples.filter((s) => s.actual === 0).slice(0, 12);
  const mixed = frauds.flatMap((f, i) => (legit[i] ? [f, legit[i]] : [f]));
  const items = mixed.map((s) => ({
    id: s.test_index,
    fraud: s.rf.label === 1,
    score: s.rf.score,
  }));
  return (
    <div className="ticker" aria-hidden="true">
      <div className="track">
        {[...items, ...items].map((it, i) => (
          <div key={i} className={`chip ${it.fraud ? "f" : ""}`}>
            #{it.id} · {it.fraud ? "FRAUD" : "legit"} {it.score.toFixed(2)}
          </div>
        ))}
      </div>
    </div>
  );
}
