import { useReducedMotion } from "motion/react";
import { useEffect, useRef } from "react";

type Segment = { text: string; gradient?: [string, string] };

const FAR = { wght: 560, wdth: 92 };
const NEAR = { wght: 1000, wdth: 132 };

const hex = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => {
  const [r1, g1, b1] = hex(a), [r2, g2, b2] = hex(b);
  return `rgb(${Math.round(r1 + (r2 - r1) * t)}, ${Math.round(g1 + (g2 - g1) * t)}, ${Math.round(b1 + (b2 - b1) * t)})`;
};

/**
 * Letters swell in weight and width as the cursor nears them (a variable-font "pressure" effect).
 * Until the visitor first moves a pointer, an invisible cursor sweeps across the line so it is alive on arrival.
 */
export default function TextPressure({ segments }: { segments: Segment[] }) {
  const root = useRef<HTMLSpanElement>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    const host = root.current;
    if (!host || reduce) return;
    const chars = Array.from(host.querySelectorAll<HTMLElement>("[data-ch]"));
    let hasPointer = false;
    let visible = true;
    const target = { x: -9999, y: -9999 };
    const cursor = { x: -9999, y: -9999 };
    const onMove = (e: PointerEvent) => {
      hasPointer = true;
      target.x = e.clientX;
      target.y = e.clientY;
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    const io = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; });
    io.observe(host);

    let raf = 0;
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      if (!visible) return;
      const box = host.getBoundingClientRect();
      if (!hasPointer) {
        target.x = box.left + box.width * (0.5 + 0.46 * Math.sin(now / 1700));
        target.y = box.top + box.height / 2;
      }
      if (cursor.x < -5000) { cursor.x = target.x; cursor.y = target.y; }
      cursor.x += (target.x - cursor.x) / 9;
      cursor.y += (target.y - cursor.y) / 9;
      // read all positions first, then write all styles (no layout thrash)
      const reach = Math.max(120, box.height * 2.4);
      const t = chars.map((el) => {
        const r = el.getBoundingClientRect();
        const d = Math.hypot(cursor.x - (r.left + r.width / 2), cursor.y - (r.top + r.height / 2));
        return Math.max(0, 1 - d / reach) ** 1.5;
      });
      chars.forEach((el, i) => {
        const w = FAR.wght + (NEAR.wght - FAR.wght) * t[i];
        const x = FAR.wdth + (NEAR.wdth - FAR.wdth) * t[i];
        el.style.fontVariationSettings = `'wght' ${w.toFixed(0)}, 'wdth' ${x.toFixed(0)}`;
      });
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      io.disconnect();
      window.removeEventListener("pointermove", onMove);
    };
  }, [reduce]);

  return (
    <span ref={root} className="tp" aria-hidden="true">
      {segments.map((seg, si) => {
        const letters = Array.from(seg.text);
        return (
          <span key={si} className="tp-seg">
            {seg.text.split(" ").map((word, wi, words) => {
              const before = seg.text.split(" ").slice(0, wi).join(" ").length + (wi ? 1 : 0);
              return (
                <span key={wi}>
                  <span className="tp-word">
                    {Array.from(word).map((ch, ci) => {
                      const idx = before + ci;
                      const color = seg.gradient ? mix(seg.gradient[0], seg.gradient[1], idx / Math.max(1, letters.length - 1)) : undefined;
                      return <span key={ci} data-ch style={{ color }} className="tp-ch">{ch}</span>;
                    })}
                  </span>
                  {wi < words.length - 1 ? " " : ""}
                </span>
              );
            })}
            {si < segments.length - 1 ? " " : ""}
          </span>
        );
      })}
    </span>
  );
}
