import { useState } from "react";
import { predict } from "./api";
import { SequenceInput } from "./components/SequenceInput";
import { PredictionResult } from "./components/PredictionResult";
import type { PredictionResponse } from "./types";
import styles from "./App.module.css";

export default function App() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(sequence: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predict(sequence);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>pre-miRNA Classifier</h1>
        <p className={styles.subtitle}>
          Predicts whether a nucleotide sequence is a genuine human pre-microRNA
          using sequence composition features and a Random Forest classifier.
        </p>
      </header>

      <main className={styles.main}>
        <section className={styles.section}>
          <SequenceInput onSubmit={handleSubmit} loading={loading} />
        </section>

        {error && (
          <div className={styles.error}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <section className={styles.section}>
            <PredictionResult result={result} />
          </section>
        )}
      </main>

      <footer className={styles.footer}>
        <p>
          Data sourced from{" "}
          <a href="https://www.ncbi.nlm.nih.gov/" target="_blank" rel="noreferrer">
            NCBI
          </a>
          . Classifier trained on 1,815 human pre-miRNA sequences.
        </p>
      </footer>
    </div>
  );
}
