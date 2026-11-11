import { motion, useReducedMotion } from "motion/react";
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  delay?: number;
  /** Distance in px the content travels in from. */
  distance?: number;
  direction?: "up" | "down" | "left" | "right";
  blur?: number;
  className?: string;
};

/**
 * Animated-content entrance: as a block scrolls into view it fades, unblurs, scales up slightly and
 * slides in from `direction` on a critically damped spring (no bounce). Plays once.
 */
export default function Reveal({ children, delay = 0, distance = 36, direction = "up", blur = 6, className }: Props) {
  const reduce = useReducedMotion();
  const from = {
    up: { y: distance }, down: { y: -distance }, left: { x: distance }, right: { x: -distance },
  }[direction];
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, scale: 0.97, filter: `blur(${blur}px)`, ...from }}
      whileInView={{ opacity: 1, scale: 1, filter: "blur(0px)", x: 0, y: 0 }}
      viewport={{ once: true, margin: "0px 0px -8% 0px" }}
      transition={{ type: "spring", bounce: 0, duration: 0.8, delay }}
    >
      {children}
    </motion.div>
  );
}
