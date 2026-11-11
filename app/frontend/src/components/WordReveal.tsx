import { motion, useReducedMotion } from "motion/react";

type Props = { text: string; className?: string; delay?: number };

/** Headline that fades and unblurs in word by word. */
export default function WordReveal({ text, className, delay = 0 }: Props) {
  const reduce = useReducedMotion();
  return (
    <span className={className} aria-label={text}>
      {text.split(" ").map((word, i) => (
        <motion.span
          key={i}
          aria-hidden="true"
          className="word"
          initial={reduce ? false : { opacity: 0, y: 18, filter: "blur(6px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ delay: delay + i * 0.09, duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }}
        >
          {word}&nbsp;
        </motion.span>
      ))}
    </span>
  );
}
