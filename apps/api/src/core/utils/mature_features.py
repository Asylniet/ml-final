"""Feature extraction for mature miRNA position prediction.

Each pre-miRNA is slid with a fixed-size window; features are extracted per window.

Structural features use the FULL hairpin fold (computed once per sequence) rather
than folding each 22-nt window in isolation. This is biologically correct: Dicer
reads pairing status in the context of the whole hairpin, not isolated fragments.
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
    + ["ctx_paired_fraction", "ctx_loop_fraction", "ctx_dist_center"]
)


def _fold_sequence(seq: str) -> str:
    """Return dot-bracket structure for seq. Empty string on failure."""
    try:
        import RNA  # noqa: PLC0415
        fc = RNA.fold_compound(seq)
        structure, _ = fc.mfe()
        return str(structure)
    except Exception:
        return "." * len(seq)


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


def _context_features(structure: str, start: int, seq_len: int) -> list[float]:
    """Pairing context from the full hairpin structure for this window.

    Folding the isolated 22-nt window is misleading — a region that is paired
    in the full hairpin may appear unpaired in isolation. These features describe
    the actual structural environment of the window within the complete pre-miRNA.
    """
    if not structure or start + WINDOW_SIZE > len(structure):
        return [0.0, 1.0, 0.5]

    window_struct = structure[start : start + WINDOW_SIZE]
    n = len(window_struct)
    paired = sum(1 for c in window_struct if c in "()")
    unpaired = n - paired

    ctx_paired = paired / max(n, 1)
    ctx_loop = unpaired / max(n, 1)

    # Normalized distance of window center from structural center
    # (mature miRNAs cluster near the stem ends, away from the terminal loop)
    window_center = start + WINDOW_SIZE / 2
    struct_center = seq_len / 2
    ctx_dist_center = abs(window_center - struct_center) / max(struct_center, 1)

    return [ctx_paired, ctx_loop, ctx_dist_center]


def extract_window_features(seq: str, start: int, full_structure: str = "") -> np.ndarray:
    """Feature vector for one window. Pass `full_structure` from `extract_all_windows`."""
    seq = seq.upper().replace("T", "U")
    window = seq[start : start + WINDOW_SIZE]
    comp = _window_composition(window)
    pos = _position_features(start, len(seq), WINDOW_SIZE)
    gc5, gc3 = _flanking_gc(seq, start)
    ctx = _context_features(full_structure, start, len(seq))
    return np.array([*comp, *pos, gc5, gc3, *ctx], dtype=float)


def extract_all_windows(seq: str) -> tuple[np.ndarray, list[int], str]:
    """Return (feature_matrix, starts, structure) for all valid windows.

    ViennaRNA is called ONCE per sequence, not once per window.
    """
    seq = seq.upper().replace("T", "U")
    structure = _fold_sequence(seq)
    starts = list(range(len(seq) - WINDOW_SIZE + 1))
    if not starts:
        return np.empty((0, len(MATURE_FEATURE_NAMES))), [], structure
    X = np.array([extract_window_features(seq, s, structure) for s in starts])
    return X, starts, structure


def predict_mature_region(seq: str, model) -> dict:
    """Slide window over seq, return best-scoring window as predicted mature miRNA."""
    seq = seq.upper().replace("T", "U")
    X, starts, _ = extract_all_windows(seq)
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
