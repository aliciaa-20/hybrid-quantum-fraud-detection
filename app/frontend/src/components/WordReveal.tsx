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
          initial={reduce ? false : { opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: "spring", bounce: 0, duration: 0.8, delay: delay + i * 0.08 }}
        >
          {word}&nbsp;
        </motion.span>
      ))}
    </span>
  );
}
