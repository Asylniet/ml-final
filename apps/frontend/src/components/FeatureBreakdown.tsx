import type { FeatureImportance } from "../types";
import styles from "./FeatureBreakdown.module.css";

interface Props {
  values: Record<string, number>;
  importances: FeatureImportance[];
}

interface BreakdownItem {
  name: string;
  value: number;
  valuePercent: number;
  rangeStart: number;
  rangeWidth: number;
  displayValue: string;
}

export function FeatureBreakdown({ values, importances }: Props) {
  const ranked = importances
    .filter((item) => item.name in values)
    .slice(0, 8)
    .map((item, index, items): BreakdownItem => {
      const value = values[item.name];
      const rankRatio = items.length > 1 ? index / (items.length - 1) : 0;
      const rangeStart = 32 + (1 - rankRatio) * 16;
      const rangeWidth = 28 - rankRatio * 10;

      return {
        name: item.name,
        value,
        valuePercent: normalizeFeatureValue(item.name, value),
        rangeStart,
        rangeWidth,
        displayValue: formatFeatureValue(item.name, value),
      };
    });

  if (ranked.length === 0) {
    return null;
  }

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Sequence profile</p>
          <h3 className={styles.title}>Top 8 influential features</h3>
        </div>
        <span className={styles.caption}>Value vs typical pre-miRNA band</span>
      </div>

      <div className={styles.rows}>
        {ranked.map((item) => (
          <div key={item.name} className={styles.row}>
            <div className={styles.rowHeader}>
              <span className={styles.name}>{item.name}</span>
              <span className={styles.value}>{item.displayValue}</span>
            </div>
            <div className={styles.track}>
              <div
                className={styles.range}
                style={{ left: `${item.rangeStart}%`, width: `${item.rangeWidth}%` }}
              />
              <div className={styles.fill} style={{ width: `${item.valuePercent}%` }} />
              <div className={styles.marker} style={{ left: `${item.valuePercent}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function normalizeFeatureValue(name: string, value: number): number {
  let scale = 1;

  if (name === "length") {
    scale = 120;
  } else if (name === "shannon_entropy") {
    scale = 2.5;
  } else if (name === "purine_pyrimidine_ratio") {
    scale = 3;
  }

  const normalized = Math.max(0, Math.min(Math.abs(value) / scale, 1));
  return normalized * 100;
}

function formatFeatureValue(name: string, value: number): string {
  if (name === "length") {
    return `${Math.round(value)} nt`;
  }
  return value.toFixed(3);
}
