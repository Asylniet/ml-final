import type { SecondaryStructure } from "../types";
import styles from "./SecondaryStructureCard.module.css";

interface Props {
  structure: SecondaryStructure;
}

export function SecondaryStructureCard({ structure }: Props) {
  return (
    <section className={styles.card}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>RNA folding</p>
          <h3 className={styles.title}>Predicted secondary structure</h3>
        </div>
        <div className={styles.meta}>
          <span className={styles.metric}>MFE {structure.mfe.toFixed(2)} kcal/mol</span>
        </div>
      </div>

      <div
        className={styles.figure}
        dangerouslySetInnerHTML={{ __html: structure.svg }}
      />

      <div className={styles.dotBlock}>
        <span className={styles.dotLabel}>Dot-bracket notation</span>
        <code className={styles.dotBracket}>{structure.dot_bracket}</code>
      </div>
    </section>
  );
}
