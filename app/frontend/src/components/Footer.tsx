import { APP_NAME } from "../config";

const ext = { target: "_blank", rel: "noopener noreferrer" } as const;

/** Slim footer: who, what it is, credits, and a way back to the top. */
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-row">
        <span><strong>{APP_NAME}</strong> · Experimental research demo. Quantum models run on a simulator. Nothing you upload is stored.</span>
        <span className="footer-links">
          <a href="https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud" {...ext}>Dataset: ULB</a>
          <a href="https://qiskit.org" {...ext}>Qiskit</a>
          <a href="https://scikit-learn.org" {...ext}>scikit-learn</a>
          <a href="#top" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); }}>Back to top ↑</a>
        </span>
      </div>
    </footer>
  );
}
