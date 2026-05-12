import type { FeatureImportance, PredictionResponse } from "../types";
import { FeatureBreakdown } from "./FeatureBreakdown";
import { NucleotideSequence } from "./NucleotideSequence";
import { SecondaryStructureCard } from "./SecondaryStructureCard";
import styles from "./PredictionResult.module.css";

interface Props {
  result: PredictionResponse;
  importances: FeatureImportance[];
}

export function PredictionResult({ result, importances }: Props) {
  return (
    <div className={styles.card}>
      <div className={`${styles.badge} ${result.is_mirna ? styles.positive : styles.negative}`}>
        {result.prediction}
      </div>

      <div className={styles.metrics}>
        <Metric label="Confidence" value={`${(result.confidence * 100).toFixed(1)}%`} />
        <Metric label="GC Content" value={`${(result.gc_content * 100).toFixed(1)}%`} />
        <Metric label="Length" value={`${result.length} nt`} />
      </div>

      <ConfidenceBar value={result.confidence} positive={result.is_mirna} />

      <div className={styles.sequenceBlock}>
        <span className={styles.seqLabel}>Sequence</span>
        <code className={styles.sequence}>
          <NucleotideSequence sequence={result.sequence} />
        </code>
      </div>

      {result.secondary_structure && (
        <SecondaryStructureCard structure={result.secondary_structure} />
      )}

      {Object.keys(result.feature_values).length > 0 && (
        <FeatureBreakdown values={result.feature_values} importances={importances} />
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.metric}>
      <span className={styles.metricValue}>{value}</span>
      <span className={styles.metricLabel}>{label}</span>
    </div>
  );
}

function ConfidenceBar({ value, positive }: { value: number; positive: boolean }) {
  return (
    <div className={styles.barTrack}>
      <div
        className={`${styles.barFill} ${positive ? styles.barPositive : styles.barNegative}`}
        style={{ width: `${value * 100}%` }}
      />
    </div>
  );
}
