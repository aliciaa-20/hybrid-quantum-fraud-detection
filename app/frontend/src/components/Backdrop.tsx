/** Fixed starfield and soft colour glows behind every page. Pure CSS, decorative only. */
export default function Backdrop() {
  return (
    <div className="backdrop" aria-hidden="true">
      <div className="stars" />
      <div className="glow g1" />
      <div className="glow g2" />
      <div className="glow g3" />
    </div>
  );
}
