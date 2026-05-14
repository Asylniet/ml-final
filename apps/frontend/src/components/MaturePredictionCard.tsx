import type { MaturePrediction } from "../types";
import styles from "./MaturePredictionCard.module.css";

interface Props {
  prediction: MaturePrediction;
  hairpinSequence: string;
}

export function MaturePredictionCard({ prediction, hairpinSequence }: Props) {
  const { mature_sequence, start, end, confidence, window_scores } = prediction;
  const seqLen = hairpinSequence.length;
  const maxScore = Math.max(...window_scores, 0.001);

  return (
    <section className={styles.card}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Mature miRNA Prediction</p>
          <h3 className={styles.title}>Predicted active miRNA sequence</h3>
        </div>
        <div className={styles.meta}>
          <span className={styles.metric}>
            {(confidence * 100).toFixed(1)}% confidence
          </span>
        </div>
      </div>

      <div className={styles.positionBar}>
        <div className={styles.positionLabel}>
          Position within pre-miRNA (nt {start + 1}–{end})
        </div>
        <div className={styles.track}>
          <div className={styles.trackBg} />
          <div
            className={styles.trackFill}
            style={{
              left: `${(start / seqLen) * 100}%`,
              width: `${((end - start) / seqLen) * 100}%`,
            }}
          />
        </div>
        <div className={styles.trackLabels}>
          <span>5'</span>
          <span>{seqLen} nt</span>
          <span>3'</span>
        </div>
      </div>

      <div className={styles.sequenceBlock}>
        <span className={styles.seqLabel}>Pre-miRNA with mature region highlighted</span>
        <code className={styles.sequence}>
          <span className={styles.flank}>{hairpinSequence.slice(0, start)}</span>
          <span className={styles.mature}>{hairpinSequence.slice(start, end)}</span>
          <span className={styles.flank}>{hairpinSequence.slice(end)}</span>
        </code>
      </div>

      <div className={styles.matureBlock}>
        <span className={styles.seqLabel}>Predicted mature miRNA</span>
        <code className={styles.matureSeq}>{mature_sequence}</code>
        <span className={styles.matureLen}>{mature_sequence.length} nt</span>
      </div>

      {window_scores.length > 1 && (
        <div className={styles.heatmapBlock}>
          <span className={styles.seqLabel}>Window score heatmap</span>
          <div className={styles.heatmap}>
            {window_scores.map((score, i) => (
              <div
                key={i}
                className={styles.heatCell}
                style={{ opacity: 0.15 + (score / maxScore) * 0.85 }}
                title={`pos ${i + 1}: ${(score * 100).toFixed(1)}%`}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
