import { useEffect, useState } from "react";
import { getFeatureImportances, getStats, predict } from "./api";
import styles from "./App.module.css";
import { FeatureImportanceChart } from "./components/FeatureImportanceChart";
import { PredictionResult } from "./components/PredictionResult";
import { SequenceInput } from "./components/SequenceInput";
import { StatsPanel } from "./components/StatsPanel";
import type { FeatureImportance, ModelStats, PredictionResponse } from "./types";

export default function App() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [stats, setStats] = useState<ModelStats | null>(null);
  const [importances, setImportances] = useState<FeatureImportance[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setDashboardLoading(true);
      setDashboardError(null);
      try {
        const [statsData, importancesData] = await Promise.all([
          getStats(),
          getFeatureImportances(),
        ]);
        if (!active) {
          return;
        }
        setStats(statsData);
        setImportances(importancesData);
      } catch (err) {
        if (!active) {
          return;
        }
        setDashboardError(err instanceof Error ? err.message : "Failed to load model data");
      } finally {
        if (active) {
          setDashboardLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      active = false;
    };
  }, []);

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
        <div className={styles.heroRow}>
          <span className={styles.heroIcon} aria-hidden="true">
            <svg viewBox="0 0 48 48" className={styles.heroSvg}>
              <path
                d="M16 7c7 0 9 7 16 7m-16 27c7 0 9-7 16-7M15 11c5 5 13 13 18 26M33 11C28 16 20 24 15 37"
                fill="none"
                stroke="currentColor"
                strokeWidth="3.4"
                strokeLinecap="round"
              />
              <path
                d="M20 18h8M18 24h12M20 30h8"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
              />
            </svg>
          </span>
          <div>
            <p className={styles.kicker}>Feature-rich sequence intelligence</p>
            <h1 className={styles.title}>pre-miRNA Classifier</h1>
          </div>
        </div>
        <p className={styles.subtitle}>
          Predicts whether a nucleotide sequence is a genuine human pre-microRNA
          using enriched composition features, tuned Random Forest inference, and
          visual feature explanations.
        </p>
      </header>

      <main className={styles.main}>
        <section className={styles.section}>
          {dashboardLoading ? (
            <div className={styles.skeletonCard}>
              <div className={styles.skeletonTitle} />
              <div className={styles.skeletonGrid}>
                <div className={styles.skeletonTile} />
                <div className={styles.skeletonTile} />
                <div className={styles.skeletonTile} />
                <div className={styles.skeletonTile} />
              </div>
            </div>
          ) : stats ? (
            <StatsPanel stats={stats} />
          ) : null}
        </section>

        <section className={styles.section}>
          {dashboardLoading ? (
            <div className={styles.skeletonCard}>
              <div className={styles.skeletonTitle} />
              <div className={styles.skeletonChart} />
            </div>
          ) : (
            <FeatureImportanceChart importances={importances} />
          )}
        </section>

        {dashboardError && (
          <div className={styles.error}>
            <strong>Model data error:</strong> {dashboardError}
          </div>
        )}

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
            <PredictionResult result={result} importances={importances} />
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
