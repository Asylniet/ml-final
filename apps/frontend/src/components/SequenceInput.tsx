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
<<<<<<< HEAD
    if (val) {
      setSequence(val);
    }
=======
    if (val) setSequence(val);
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
    e.target.value = "";
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = sequence.trim();
<<<<<<< HEAD
    if (cleaned) {
      onSubmit(cleaned);
    }
=======
    if (cleaned) onSubmit(cleaned);
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.header}>
        <label htmlFor="sequence" className={styles.label}>
          Nucleotide sequence
        </label>
        <select onChange={handleExample} className={styles.examples} defaultValue="">
          <option value="" disabled>
<<<<<<< HEAD
            Load example...
=======
            Load example…
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
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
<<<<<<< HEAD
        placeholder="Enter a sequence of A, U, G, C (or T)..."
=======
        placeholder="Enter a sequence of A, U, G, C (or T)…"
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
        rows={5}
        spellCheck={false}
      />

<<<<<<< HEAD
      <p className={styles.hint}>Valid characters: A, U, G, C, T | Min length: 10 nt</p>

      <button type="submit" className={styles.button} disabled={loading || !sequence.trim()}>
        {loading ? (
          <span className={styles.buttonInner}>
            <span className={styles.spinner} aria-hidden="true" />
            Predicting...
          </span>
        ) : (
          "Predict"
        )}
=======
      <p className={styles.hint}>
        Valid characters: A, U, G, C, T &nbsp;·&nbsp; Min length: 10 nt
      </p>

      <button type="submit" className={styles.button} disabled={loading || !sequence.trim()}>
        {loading ? "Predicting…" : "Predict"}
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
      </button>
    </form>
  );
}
