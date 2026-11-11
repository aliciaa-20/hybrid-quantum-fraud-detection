import Reveal from "../components/Reveal";

const STEPS = [
  { n: "1", title: "The data", text: "283,726 real card transactions after removing duplicates, only 473 of them fraud (0.17%). The features are anonymized, so there is no merchant or amount to read." },
  { n: "2", title: "Pick 4 features", text: "Mutual information keeps 4 of the 30 features (V10, V12, V14, V17). Four features map neatly onto four qubits." },
  { n: "3", title: "Balance the classes", text: "SMOTE and ADASYN invent extra fraud examples for training only. The test set is never touched." },
  { n: "4", title: "Compare the models", text: "Random Forest, SVM and Logistic Regression against two quantum models: a kernel method (QSVM) and a variational classifier (VQC)." },
];

const CARDS = [
  { title: "What “experimental” means", text: "QSVM and VQC run on a simulator and are slow, so this site limits them to small batches. The VQC in the sample browser is the paper's own run; the live VQC is a seeded re-run and can differ slightly because VQC training is random." },
  { title: "Honest limits", text: "Quantum models ran on a simulator, not real hardware. QSVM was evaluated on a small matched subset that is about 38% fraud. Tuned thresholds were chosen using the test labels. Treat the numbers as research results, not a product benchmark." },
  { title: "Your data", text: "Uploaded files are scored in memory and discarded. Nothing is stored, logged or used for training." },
  { title: "Data and credits", text: "Credit Card Fraud Detection dataset from the Machine Learning Group at ULB (Université Libre de Bruxelles), via Kaggle. Built with Qiskit, scikit-learn, FastAPI and React." },
];

export default function About() {
  return (
    <section className="page">
      <h1>About</h1>
      <p className="lede small-lede">
        An honors project that asks a simple question: can quantum machine learning catch credit card fraud better than
        classical methods? It does not claim it can. In the project's own results, a classical Random Forest wins.
      </p>

      <Reveal><h2 className="section-title">How it works</h2></Reveal>
      <div className="steps">
        {STEPS.map((s, i) => (
          <Reveal key={s.n} delay={i * 0.07} className="step">
            <span className="step-n">{s.n}</span>
            <h3>{s.title}</h3>
            <p>{s.text}</p>
          </Reveal>
        ))}
      </div>

      <Reveal><h2 className="section-title">Good to know</h2></Reveal>
      <div className="about-cards">
        {CARDS.map((c, i) => (
          <Reveal key={c.title} delay={i * 0.07} className="note">
            <strong>{c.title}</strong>
            <p>{c.text}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
