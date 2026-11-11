import { useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";

const POOL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&@$";
const rand = () => POOL[Math.floor(Math.random() * POOL.length)];

type Props = { text: string; run: number | string; delay?: number; duration?: number };

/** Letters scramble through random glyphs, then lock in left to right. */
export default function DecryptedText({ text, run, delay = 0, duration = 850 }: Props) {
  const reduce = useReducedMotion();
  const [cells, setCells] = useState(() => Array.from(text, (ch) => ({ ch: reduce ? ch : rand(), done: Boolean(reduce) })));

  useEffect(() => {
    if (reduce) {
      setCells(Array.from(text, (ch) => ({ ch, done: true })));
      return;
    }
    const start = performance.now() + delay;
    const id = window.setInterval(() => {
      const t = performance.now() - start;
      const n = text.length;
      setCells(Array.from(text, (ch, i) => (t >= ((i + 1) / n) * duration ? { ch, done: true } : { ch: rand(), done: false })));
      if (t >= duration) window.clearInterval(id);
    }, 45);
    return () => window.clearInterval(id);
  }, [text, run, delay, duration, reduce]);

  return (
    <span className="dec" aria-label={text}>
      {cells.map((c, i) => (
        <span key={i} aria-hidden="true" className={`dc ${c.done ? "done" : ""}`}>{c.ch}</span>
      ))}
    </span>
  );
}
