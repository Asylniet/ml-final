import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FeatureImportance } from "../types";
import styles from "./FeatureImportanceChart.module.css";

interface Props {
  importances: FeatureImportance[];
}

function getFeatureColor(name: string): string {
  if (name.endsWith("_freq") && name.length === 6) {
    return "#0ea5e9";
  }
  if (name.endsWith("_freq") && name.length === 7) {
    return "#8b5cf6";
  }
  if (name.endsWith("_freq") && name.length === 8) {
    return "#4f46e5";
  }
  return "#94a3b8";
}

export function FeatureImportanceChart({ importances }: Props) {
  const data = importances.slice(0, 15).map((item) => ({
    ...item,
    shortName: item.name.replace("_freq", ""),
    color: getFeatureColor(item.name),
  }));

  if (data.length === 0) {
    return (
      <div className={styles.card}>
        <div className={styles.header}>
          <div>
            <p className={styles.eyebrow}>Explainability</p>
            <h2 className={styles.title}>Top feature importances</h2>
          </div>
        </div>
        <p className={styles.empty}>Feature importances will appear after the model loads.</p>
      </div>
    );
  }

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Explainability</p>
          <h2 className={styles.title}>Top feature importances</h2>
        </div>
        <div className={styles.legend}>
          <LegendPill label="NT" color="#0ea5e9" />
          <LegendPill label="Dinuc" color="#8b5cf6" />
          <LegendPill label="Trinuc" color="#4f46e5" />
          <LegendPill label="Other" color="#94a3b8" />
        </div>
      </div>

      <div className={styles.chartWrap}>
        <ResponsiveContainer width="100%" height={360}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 24, left: 12, bottom: 8 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--color-border)"
              horizontal={false}
            />
            <XAxis type="number" tick={{ fill: "var(--color-muted)", fontSize: 12 }} />
            <YAxis
              dataKey="shortName"
              type="category"
              width={92}
              tick={{ fill: "var(--color-text)", fontSize: 12 }}
            />
            <Tooltip
              cursor={{ fill: "color-mix(in srgb, var(--color-accent-2) 10%, transparent)" }}
              formatter={(value) =>
                typeof value === "number" ? value.toFixed(4) : String(value ?? "")
              }
            />
            <Bar dataKey="importance" radius={[0, 10, 10, 0]}>
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function LegendPill({ label, color }: { label: string; color: string }) {
  return (
    <span className={styles.legendPill}>
      <span className={styles.legendDot} style={{ backgroundColor: color }} />
      {label}
    </span>
  );
}
