import itertools
import math

import numpy as np

_NUCLEOTIDES = ["A", "U", "G", "C"]
_DINUCLEOTIDES = ["".join(p) for p in itertools.product(_NUCLEOTIDES, repeat=2)]
_TRINUCLEOTIDES = ["".join(p) for p in itertools.product(_NUCLEOTIDES, repeat=3)]


def _structure_features(seq: str, gc_content: float, n: int) -> list[float]:
    """Compute ViennaRNA secondary structure features.

    MFE and paired-fraction are the strongest discriminators for pre-miRNA
    (Zhang et al. 2006; Batuwita & Palade 2009).
    Returns zeros if ViennaRNA is unavailable.
    """
    try:
        import RNA  # noqa: PLC0415
        fc = RNA.fold_compound(seq)
        structure, mfe = fc.mfe()
        mfe = float(mfe)
        paired = sum(1 for c in structure if c in "()")
        paired_fraction = paired / max(n, 1)
        amfe = (mfe / max(n, 1)) * 100        # adjusted MFE (per 100 nt)
        mfei = amfe / gc_content if gc_content > 0 else 0.0  # MFE efficiency index
    except Exception:
        mfe, paired_fraction, amfe, mfei = 0.0, 0.0, 0.0, 0.0
    return [mfe, paired_fraction, amfe, mfei]


def extract_features(sequence: str) -> np.ndarray:
    seq = sequence.upper().replace("T", "U")
    n = len(seq)
    safe_n = max(n, 1)

    nt_counts = {nt: seq.count(nt) for nt in _NUCLEOTIDES}
    nt_freqs = [nt_counts[nt] / safe_n for nt in _NUCLEOTIDES]
    gc_content = (nt_counts["G"] + nt_counts["C"]) / safe_n
    au_content = (nt_counts["A"] + nt_counts["U"]) / safe_n

    dinuc_freqs = []
    total_dinuc = n - 1 if n > 1 else 1
    for di in _DINUCLEOTIDES:
        count = sum(1 for i in range(n - 1) if seq[i : i + 2] == di)
        dinuc_freqs.append(count / total_dinuc)

    trinuc_freqs = []
    total_trinuc = n - 2 if n > 2 else 1
    for tri in _TRINUCLEOTIDES:
        count = sum(1 for i in range(n - 2) if seq[i : i + 3] == tri)
        trinuc_freqs.append(count / total_trinuc)

    shannon_entropy = -sum(freq * math.log2(freq) for freq in nt_freqs if freq > 0)

    purine_count = nt_counts["A"] + nt_counts["G"]
    pyrimidine_count = nt_counts["C"] + nt_counts["U"]
    purine_pyrimidine_ratio = purine_count / pyrimidine_count if pyrimidine_count else 0.0

    gu_wobble_count = sum(1 for i in range(n - 1) if seq[i : i + 2] == "GU")
    gu_wobble_freq = gu_wobble_count / total_dinuc

    struct_feats = _structure_features(seq, gc_content, n)

    return np.array(
        [
            n,
            gc_content,
            au_content,
            *nt_freqs,
            *dinuc_freqs,
            *trinuc_freqs,
            shannon_entropy,
            purine_pyrimidine_ratio,
            gu_wobble_freq,
            *struct_feats,
        ],
        dtype=float,
    )

FEATURE_NAMES = (
    ["length", "gc_content", "au_content"]
    + [f"{nt}_freq" for nt in _NUCLEOTIDES]
    + [f"{di}_freq" for di in _DINUCLEOTIDES]
    + [f"{tri}_freq" for tri in _TRINUCLEOTIDES]
    + ["shannon_entropy", "purine_pyrimidine_ratio", "gu_wobble_freq"]
    + ["mfe", "paired_fraction", "amfe", "mfei"]
)
