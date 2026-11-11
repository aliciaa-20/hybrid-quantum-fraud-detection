import { APP_NAME } from "../config";

/** Slim footer: what this is, and a way back to the top. Credits live on the About page. */
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-row">
        <span><strong>{APP_NAME}</strong> · Experimental research demo. Quantum models run on a simulator. Nothing you upload is stored.</span>
        <span className="footer-links">
          <a href="#top" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); }}>Back to top ↑</a>
        </span>
      </div>
    </footer>
  );
}
