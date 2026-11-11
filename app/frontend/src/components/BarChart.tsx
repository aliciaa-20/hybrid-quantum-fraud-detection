import { motion } from "motion/react";

type Bar = { label: string; value: number };

const money = (n: number) => `${n < 0 ? "−" : "+"}$${Math.abs(Math.round(n)).toLocaleString("en-US")}`;

/** Diverging bars around a zero line: gains grow up, losses grow down. Axis labels sit on their own row. */
export default function BarChart({ bars }: { bars: Bar[] }) {
  const max = Math.max(1, ...bars.map((b) => Math.abs(b.value)));
  return (
    <div className="barchart" role="img" aria-label={bars.map((b) => `${b.label} ${money(b.value)}`).join(", ")}>
      <div className="bplot">
        <div className="zero" />
        {bars.map((b, i) => {
          const pct = (Math.abs(b.value) / max) * 38;
          const neg = b.value < 0;
          return (
            <div key={b.label} className="bcol">
              <motion.div
                className={`bbar ${neg ? "neg" : "pos"}`}
                style={{ height: `${pct}%`, transformOrigin: neg ? "top" : "bottom" }}
                initial={{ scaleY: 0 }}
                whileInView={{ scaleY: 1 }}
                viewport={{ once: true, margin: "0px 0px -10% 0px" }}
                transition={{ type: "spring", bounce: 0.1, duration: 1, delay: i * 0.1 }}
              />
              <span className={`bval ${neg ? "bad" : "good"}`} style={neg ? { top: `calc(50% + ${pct}% + 6px)` } : { bottom: `calc(50% + ${pct}% + 6px)` }}>
                {money(b.value)}
              </span>
            </div>
          );
        })}
      </div>
      <div className="baxis">{bars.map((b) => <span key={b.label}>{b.label}</span>)}</div>
    </div>
  );
}
