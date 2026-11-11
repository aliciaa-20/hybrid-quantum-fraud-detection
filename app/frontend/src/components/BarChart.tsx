import { motion } from "motion/react";

type Bar = { label: string; value: number };

const money = (n: number) => `${n < 0 ? "−" : "+"}$${Math.abs(Math.round(n)).toLocaleString("en-US")}`;

/** Diverging bars around a zero line: gains grow up, losses grow down. Animates in when scrolled to. */
export default function BarChart({ bars }: { bars: Bar[] }) {
  const max = Math.max(1, ...bars.map((b) => Math.abs(b.value)));
  return (
    <div className="barchart" role="img" aria-label={bars.map((b) => `${b.label} ${money(b.value)}`).join(", ")}>
      <div className="zero" />
      {bars.map((b, i) => {
        const pct = (Math.abs(b.value) / max) * 46;
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
            <span className={`bval ${neg ? "bad" : "good"}`} style={neg ? { top: `calc(50% + ${pct}% + 4px)` } : { bottom: `calc(50% + ${pct}% + 4px)` }}>
              {money(b.value)}
            </span>
            <span className="blab">{b.label}</span>
          </div>
        );
      })}
    </div>
  );
}
