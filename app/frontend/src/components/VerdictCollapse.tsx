import { motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";
import DecryptedText from "./DecryptedText";

type Props = { label: 0 | 1; score: number; run: number | string; delay?: number; big?: boolean };

/** The verdict decrypts out of scrambled letters, then the colour and probability meter settle. */
export default function VerdictCollapse({ label, score, run, delay = 0, big }: Props) {
  const reduce = useReducedMotion();
  const [done, setDone] = useState(Boolean(reduce));

  useEffect(() => {
    if (reduce) {
      setDone(true);
      return;
    }
    setDone(false);
    const t = window.setTimeout(() => setDone(true), 900 + delay);
    return () => window.clearTimeout(t);
  }, [run, delay, reduce]);

  return (
    <div className={`vc ${big ? "big" : ""}`}>
      <div className={`verdict ${done ? (label === 1 ? "bad" : "good") : "q"}`}>
        <DecryptedText text={label === 1 ? "FRAUD" : "LEGIT"} run={run} delay={delay} />
      </div>
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
