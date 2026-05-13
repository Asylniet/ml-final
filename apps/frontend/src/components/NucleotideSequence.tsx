import styles from "./NucleotideSequence.module.css";

const NUCLEOTIDE_CLASS: Record<string, string> = {
  A: styles.a,
  U: styles.u,
  G: styles.g,
  C: styles.c,
};

interface Props {
  sequence: string;
}

export function NucleotideSequence({ sequence }: Props) {
  return (
    <>
      {sequence.split("").map((nucleotide, index) => (
        <span
          key={`${nucleotide}-${index}`}
          className={`${styles.base} ${NUCLEOTIDE_CLASS[nucleotide] ?? ""}`}
        >
          {nucleotide}
        </span>
      ))}
    </>
  );
}
