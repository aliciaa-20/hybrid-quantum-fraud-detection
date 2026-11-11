import { motion } from "motion/react";

type Item = { label: string; hint: string; value: number };

/** Horizontal 0 to 1 bars with a plain-language hint under each label. Widths spring to new values. */
export default function MetricBars({ items }: { items: Item[] }) {
  return (
    <div className="mbars">
      {items.map((it) => (
        <div key={it.label} className="mbar">
          <div className="mbar-top">
            <strong>{it.label}</strong>
            <span className="mbar-val">{it.value.toFixed(2)}</span>
          </div>
          <div className="mbar-track" aria-hidden="true">
            <motion.i initial={{ width: 0 }} animate={{ width: `${Math.max(1, it.value * 100)}%` }} transition={{ type: "spring", bounce: 0, duration: 0.7 }} />
          </div>
          <span className="muted small">{it.hint}</span>
        </div>
      ))}
    </div>
  );
}
