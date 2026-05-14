"""Feature extraction for mature miRNA position prediction.

Each pre-miRNA is slid with a fixed-size window; features are extracted per window.
"""

import itertools
import math

import numpy as np

WINDOW_SIZE = 22

_NUCLEOTIDES = ["A", "U", "G", "C"]
_DINUCLEOTIDES = ["".join(p) for p in itertools.product(_NUCLEOTIDES, repeat=2)]

MATURE_FEATURE_NAMES = (
    [f"w_{nt}_freq" for nt in _NUCLEOTIDES]
    + [f"w_{di}_freq" for di in _DINUCLEOTIDES]
    + ["w_gc_content", "w_au_content", "w_entropy", "w_gu_wobble"]
    + ["pos_rel", "pos_from_5", "pos_from_3", "pos_dist_center"]
    + ["flank5_gc", "flank3_gc"]
    + ["w_mfe", "w_paired_fraction", "w_amfe"]
)


def _window_composition(window: str) -> list[float]:
    n = len(window)
    safe_n = max(n, 1)

    nt_counts = {nt: window.count(nt) for nt in _NUCLEOTIDES}
    nt_freqs = [nt_counts[nt] / safe_n for nt in _NUCLEOTIDES]

    dinuc_freqs = []
    total_dinuc = max(n - 1, 1)
    for di in _DINUCLEOTIDES:
        count = sum(1 for i in range(n - 1) if window[i : i + 2] == di)
        dinuc_freqs.append(count / total_dinuc)

    gc = (nt_counts["G"] + nt_counts["C"]) / safe_n
    au = (nt_counts["A"] + nt_counts["U"]) / safe_n
    entropy = -sum(f * math.log2(f) for f in nt_freqs if f > 0)
    gu = sum(1 for i in range(n - 1) if window[i : i + 2] == "GU") / total_dinuc

    return [*nt_freqs, *dinuc_freqs, gc, au, entropy, gu]


def _position_features(start: int, seq_len: int, window_size: int) -> list[float]:
    max_start = max(seq_len - window_size, 1)
    rel_pos = start / max_start
    from_5 = start / max(seq_len, 1)
    from_3 = max(seq_len - start - window_size, 0) / max(seq_len, 1)
    center = max_start / 2
    dist_center = abs(start - center) / max(center, 1)
    return [rel_pos, from_5, from_3, dist_center]


def _flanking_gc(seq: str, start: int, flank: int = 5) -> tuple[float, float]:
    left = seq[max(0, start - flank) : start]
    right = seq[start + WINDOW_SIZE : start + WINDOW_SIZE + flank]
    gc5 = (left.count("G") + left.count("C")) / max(len(left), 1)
    gc3 = (right.count("G") + right.count("C")) / max(len(right), 1)
    return gc5, gc3


def _window_structure(window: str) -> list[float]:
    """ViennaRNA features for a short window. Zeros on failure."""
    try:
        import RNA  # noqa: PLC0415
        fc = RNA.fold_compound(window)
        structure, mfe = fc.mfe()
        mfe = float(mfe)
        paired = sum(1 for c in structure if c in "()")
        paired_fraction = paired / max(len(window), 1)
        amfe = (mfe / max(len(window), 1)) * 100
    except Exception:
        mfe, paired_fraction, amfe = 0.0, 0.0, 0.0
    return [mfe, paired_fraction, amfe]


def extract_window_features(seq: str, start: int) -> np.ndarray:
    """Feature vector for one window at position `start` in `seq`."""
    seq = seq.upper().replace("T", "U")
    window = seq[start : start + WINDOW_SIZE]
    comp = _window_composition(window)
    pos = _position_features(start, len(seq), WINDOW_SIZE)
    gc5, gc3 = _flanking_gc(seq, start)
    struct = _window_structure(window)
    return np.array([*comp, *pos, gc5, gc3, *struct], dtype=float)


def extract_all_windows(seq: str) -> tuple[np.ndarray, list[int]]:
    """Return (feature_matrix, starts) for all valid windows in seq."""
    seq = seq.upper().replace("T", "U")
    starts = list(range(len(seq) - WINDOW_SIZE + 1))
    if not starts:
        return np.empty((0, len(MATURE_FEATURE_NAMES))), []
    X = np.array([extract_window_features(seq, s) for s in starts])
    return X, starts


def predict_mature_region(seq: str, model) -> dict:
    """Slide window over seq, return best-scoring window as predicted mature miRNA."""
    seq = seq.upper().replace("T", "U")
    X, starts = extract_all_windows(seq)
    if len(starts) == 0:
        return {
            "mature_sequence": "",
            "start": 0,
            "end": 0,
            "confidence": 0.0,
            "window_scores": [],
        }

    probas = model.predict_proba(X)
    pos_class_idx = list(model.classes_).index(1)
    scores = probas[:, pos_class_idx].tolist()

    best_idx = int(np.argmax(scores))
    best_start = starts[best_idx]
    best_end = best_start + WINDOW_SIZE

    return {
        "mature_sequence": seq[best_start:best_end],
        "start": best_start,
        "end": best_end,
        "confidence": round(scores[best_idx], 4),
        "window_scores": [round(s, 4) for s in scores],
    }
