import { motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";

type Props = { label: 0 | 1; score: number; run: number | string; delay?: number; big?: boolean };

/** A verdict that flickers between "Fraud?" and "Legit?" (superposition), then collapses to the real result. */
export default function VerdictCollapse({ label, score, run, delay = 0, big }: Props) {
  const reduce = useReducedMotion();
  const [done, setDone] = useState(Boolean(reduce));
  const [flip, setFlip] = useState(false);

  useEffect(() => {
    if (reduce) {
      setDone(true);
      return;
    }
    setDone(false);
    const iv = window.setInterval(() => setFlip((f) => !f), 110);
    const t = window.setTimeout(() => {
      window.clearInterval(iv);
      setDone(true);
    }, 900 + delay);
    return () => {
      window.clearInterval(iv);
      window.clearTimeout(t);
    };
  }, [run, delay, reduce]);

  return (
    <div className={`vc ${big ? "big" : ""}`}>
      {done ? (
        <motion.div
          key="done"
          className={`verdict ${label === 1 ? "bad" : "good"}`}
          initial={reduce ? false : { scale: 0.6, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", bounce: 0.2, duration: 0.5 }}
        >
          {label === 1 ? "Fraud" : "Legit"}
        </motion.div>
      ) : (
        <div className="verdict q wobble" aria-live="polite">{flip ? "Legit?" : "Fraud?"}</div>
      )}
      <div className="meter" aria-hidden="true">
        <motion.i
          initial={false}
          animate={{ width: done ? `${Math.max(2, Math.round(score * 100))}%` : "0%" }}
          transition={{ type: "spring", bounce: 0, duration: 0.8 }}
        />
      </div>
      <div className="muted small">Fraud probability {done ? `${(score * 100).toFixed(1)}%` : "…"}</div>
    </div>
  );
}
