import itertools

import numpy as np

_NUCLEOTIDES = ["A", "U", "G", "C"]
_DINUCLEOTIDES = ["".join(p) for p in itertools.product(_NUCLEOTIDES, repeat=2)]


def extract_features(sequence: str) -> np.ndarray:
    """Extract numerical features from a nucleotide sequence (A/U/G/C)."""
    seq = sequence.upper().replace("T", "U")
    n = len(seq)

    nt_counts = {nt: seq.count(nt) for nt in _NUCLEOTIDES}
    nt_freqs = [nt_counts[nt] / n for nt in _NUCLEOTIDES]
    gc_content = (nt_counts["G"] + nt_counts["C"]) / n
    au_content = (nt_counts["A"] + nt_counts["U"]) / n

    dinuc_freqs = []
    total_dinuc = n - 1 if n > 1 else 1
    for di in _DINUCLEOTIDES:
        count = sum(1 for i in range(n - 1) if seq[i : i + 2] == di)
        dinuc_freqs.append(count / total_dinuc)

    return np.array([n, gc_content, au_content, *nt_freqs, *dinuc_freqs], dtype=float)


FEATURE_NAMES = (
    ["length", "gc_content", "au_content"]
    + [f"{nt}_freq" for nt in _NUCLEOTIDES]
    + [f"{di}_freq" for di in _DINUCLEOTIDES]
)
