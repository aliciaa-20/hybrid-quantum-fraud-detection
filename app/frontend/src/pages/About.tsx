export default function About() {
  return (
    <section className="page prose">
      <h1>About</h1>
      <p>
        This is the working demo of an honors project on hybrid quantum machine learning for credit card fraud
        detection. It does not claim quantum advantage. In the project's own results, a classical Random Forest
        beats the quantum models.
      </p>
      <h3>Method</h3>
      <p>
        Mutual information selects 4 of the 30 features (V10, V12, V14, V17), which map to 4 qubits. Classes are
        balanced with SMOTE or ADASYN on training data only. Models: Random Forest, a quantum kernel SVM (QSVM) and a
        Variational Quantum Classifier (VQC). Quantum models run on a simulator, not real quantum hardware.
      </p>
      <h3>What "experimental" means</h3>
      <p>
        QSVM and VQC are slow and limited to small batches here. The VQC stored in the sample browser is the paper's
        own run. The live VQC is a seeded re-run, so it can differ slightly, because VQC training is stochastic.
      </p>
      <h3>Data</h3>
      <p>
        The Credit Card Fraud Detection dataset from the Machine Learning Group at ULB (Université Libre de
        Bruxelles), via Kaggle. Its features are anonymized PCA components, so individual values carry no
        human-readable meaning. Uploaded files are scored and discarded.
      </p>
    </section>
  );
}
