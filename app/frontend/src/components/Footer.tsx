import { Link, useNavigate } from "react-router-dom";
import { APP_NAME } from "../config";
import StarButton from "./StarButton";

const ext = { target: "_blank", rel: "noopener noreferrer" } as const;

/** Closing call to action, link columns, small print and a big cropped wordmark. */
export default function Footer() {
  const navigate = useNavigate();
  return (
    <footer className="site-footer">
      <div className="footer-card">
        <div className="footer-cta">
          <div>
            <h2>Think you can fool it?</h2>
            <p>Drop in a few transactions and watch three models vote.</p>
          </div>
          <StarButton onClick={() => navigate("/upload")}>Try an upload →</StarButton>
        </div>

        <div className="footer-grid">
          <div className="fbrand">
            <strong>{APP_NAME}</strong>
            <p>Classical against quantum machine learning at catching credit card fraud. An honors project.</p>
          </div>
          <nav aria-label="Explore">
            <h4>Explore</h4>
            <Link to="/explore">Browse transactions</Link>
            <Link to="/upload">Upload a CSV</Link>
            <Link to="/findings">Findings</Link>
          </nav>
          <nav aria-label="The project">
            <h4>The project</h4>
            <Link to="/about">How it works</Link>
            <Link to="/about">Honest limits</Link>
            <Link to="/findings">Read before quoting</Link>
          </nav>
          <nav aria-label="Credits">
            <h4>Credits</h4>
            <a href="https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud" {...ext}>ULB fraud dataset</a>
            <a href="https://qiskit.org" {...ext}>Qiskit</a>
            <a href="https://scikit-learn.org" {...ext}>scikit-learn</a>
          </nav>
        </div>

        <div className="footer-bar">
          <span>Experimental research demo. Quantum models run on a simulator. Nothing you upload is stored.</span>
          <button className="secondary" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>Back to top ↑</button>
        </div>
        <div className="footer-mark" aria-hidden="true">NICE TRY</div>
      </div>
    </footer>
  );
}
