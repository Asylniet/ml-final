import type { ModelStats } from "../types";
import styles from "./StatsPanel.module.css";

interface Props {
  stats: ModelStats;
}

export function StatsPanel({ stats }: Props) {
  const positiveShare = stats.n_samples ? (stats.n_positive / stats.n_samples) * 100 : 0;
  const negativeShare = 100 - positiveShare;

  return (
    <div className={styles.panel}>
      <div className={styles.topRow}>
        <div>
          <p className={styles.eyebrow}>Model snapshot</p>
          <h2 className={styles.title}>Training performance at a glance</h2>
        </div>
        <span className={styles.badge}>{stats.model_type}</span>
      </div>

      <div className={styles.grid}>
        <StatCard label="Accuracy" value={`${(stats.accuracy * 100).toFixed(1)}%`} />
        <StatCard label="F1 Score" value={`${(stats.f1 * 100).toFixed(1)}%`} />
        <StatCard label="Training Samples" value={stats.n_samples.toLocaleString()} />
        <StatCard label="Features" value={stats.n_features.toString()} />
      </div>

      <div className={styles.meta}>
        <div className={styles.dataset}>
          <div className={styles.datasetHeader}>
            <span>Dataset composition</span>
            <span>
              {stats.n_positive} positive / {stats.n_negative} negative
            </span>
          </div>
          <div className={styles.datasetBar}>
            <div className={styles.datasetPositive} style={{ width: `${positiveShare}%` }} />
            <div className={styles.datasetNegative} style={{ width: `${negativeShare}%` }} />
          </div>
        </div>

        <div className={styles.metrics}>
          <Metric label="Precision" value={`${(stats.precision * 100).toFixed(1)}%`} />
          <Metric label="Recall" value={`${(stats.recall * 100).toFixed(1)}%`} />
          <Metric label="CV F1" value={`${(stats.cv_score * 100).toFixed(1)}%`} />
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.card}>
      <span className={styles.cardValue}>{value}</span>
      <span className={styles.cardLabel}>{label}</span>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.metric}>
      <span className={styles.metricLabel}>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
