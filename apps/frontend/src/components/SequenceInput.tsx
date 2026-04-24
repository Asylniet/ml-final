import { useState } from "react";
import styles from "./SequenceInput.module.css";

const EXAMPLES: Record<string, string> = {
  "hsa-let-7a-1 (pre-miRNA)":
    "UGAGGUAGUAGGUUGUAUAGUUUAGGGUCACACCCACCACUGGGAGAUAACUAUACAAUCUACUGUCUUUCCUA",
  "hsa-mir-21 (pre-miRNA)":
    "UGUCGGGUAGCUUAUCAGACUGAUGUUGACUGUUGAAUCUCAUGGCAACACCAGUCGAUGGGCUGU",
  "Poly-A (negative control)":
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
};

interface Props {
  onSubmit: (sequence: string) => void;
  loading: boolean;
}

export function SequenceInput({ onSubmit, loading }: Props) {
  const [sequence, setSequence] = useState("");

  function handleExample(e: React.ChangeEvent<HTMLSelectElement>) {
    const val = EXAMPLES[e.target.value];
    if (val) setSequence(val);
    e.target.value = "";
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = sequence.trim();
    if (cleaned) onSubmit(cleaned);
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.header}>
        <label htmlFor="sequence" className={styles.label}>
          Nucleotide sequence
        </label>
        <select onChange={handleExample} className={styles.examples} defaultValue="">
          <option value="" disabled>
            Load example…
          </option>
          {Object.keys(EXAMPLES).map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>

      <textarea
        id="sequence"
        className={styles.textarea}
        value={sequence}
        onChange={(e) => setSequence(e.target.value)}
        placeholder="Enter a sequence of A, U, G, C (or T)…"
        rows={5}
        spellCheck={false}
      />

      <p className={styles.hint}>
        Valid characters: A, U, G, C, T &nbsp;·&nbsp; Min length: 10 nt
      </p>

      <button type="submit" className={styles.button} disabled={loading || !sequence.trim()}>
        {loading ? "Predicting…" : "Predict"}
      </button>
    </form>
  );
}
