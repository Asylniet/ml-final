from pathlib import Path
from tempfile import NamedTemporaryFile

import RNA


def predict_secondary_structure(sequence: str) -> tuple[str, float]:
    """Predict the MFE secondary structure for an RNA sequence."""
    fold_compound = RNA.fold_compound(sequence)
    structure, mfe = fold_compound.mfe()
    return str(structure), float(mfe)


def render_structure_svg(sequence: str, structure: str) -> str:
    """Render an RNA secondary structure plot as SVG."""
    with NamedTemporaryFile(suffix=".svg", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        success = RNA.svg_rna_plot(sequence, structure, str(tmp_path))
        if success != 1:
            raise ValueError("ViennaRNA failed to render SVG output")
        return tmp_path.read_text(encoding="utf-8")
    finally:
        tmp_path.unlink(missing_ok=True)


def build_structure_payload(sequence: str) -> dict[str, str | float]:
    structure, mfe = predict_secondary_structure(sequence)
    svg = render_structure_svg(sequence, structure)
    return {"dot_bracket": structure, "mfe": mfe, "svg": svg}
