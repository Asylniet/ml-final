"""Download human pre-miRNA data from NCBI in GenBank format and extract mature miRNA positions.

NCBI GenBank records for pre-miRNA contain miRNA feature annotations with exact
mature miRNA coordinates — no dependency on miRBase FTP.

Output: src/data/mirbase_dataset.csv
Columns: hairpin_id, hairpin_sequence, mature_start, mature_length, arm
"""

import pathlib
import re
import time
import urllib.parse
import urllib.request

DATA_DIR = pathlib.Path(__file__).parent.parent / "src" / "data"
GENBANK_CACHE = DATA_DIR / "mirbase_hairpin.gb"
DATASET_CSV = DATA_DIR / "mirbase_dataset.csv"

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
VALID_NUCLEOTIDES = set("AUGC")
BATCH_SIZE = 100  # GenBank records are larger than FASTA, use smaller batches


# ---------------------------------------------------------------------------
# NCBI fetch helpers
# ---------------------------------------------------------------------------

def ncbi_search(term: str, retmax: int = 3000) -> list[str]:
    params = urllib.parse.urlencode({
        "db": "nuccore",
        "term": term,
        "retmax": retmax,
        "retmode": "json",
    })
    url = f"{NCBI_BASE}/esearch.fcgi?{params}"
    print(f"Searching NCBI: {term!r} ...")
    with urllib.request.urlopen(url, timeout=30) as resp:
        import json
        data = json.loads(resp.read())
    ids = data["esearchresult"]["idlist"]
    print(f"Found {len(ids)} entries")
    return ids


def ncbi_fetch_genbank(ids: list[str]) -> str:
    chunks = [ids[i : i + BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)]
    all_gb: list[str] = []
    for n, chunk in enumerate(chunks, 1):
        print(f"  Fetching GenBank batch {n}/{len(chunks)} ({len(chunk)} records)...")
        params = urllib.parse.urlencode({
            "db": "nuccore",
            "id": ",".join(chunk),
            "rettype": "gb",
            "retmode": "text",
        })
        url = f"{NCBI_BASE}/efetch.fcgi?{params}"
        with urllib.request.urlopen(url, timeout=60) as resp:
            all_gb.append(resp.read().decode("utf-8"))
        time.sleep(0.4)  # NCBI rate limit
    return "\n".join(all_gb)


# ---------------------------------------------------------------------------
# GenBank parser
# ---------------------------------------------------------------------------

def _parse_location(loc_str: str) -> tuple[int, int] | None:
    """'13..35' or 'complement(13..35)' → (0-indexed start, length) or None."""
    s = loc_str.strip()
    s = re.sub(r"complement\((.+)\)", r"\1", s)
    s = re.sub(r"join\(([^,]+),.+\)", r"\1", s)
    s = s.replace("<", "").replace(">", "")
    m = re.match(r"(\d+)\.\.(\d+)$", s)
    if m:
        start1 = int(m.group(1))
        end1 = int(m.group(2))
        return start1 - 1, end1 - start1 + 1  # 0-indexed start, length
    return None


def parse_genbank(text: str) -> list[tuple[str, str, int, int, str]]:
    """Parse GenBank text. Return (hairpin_id, hairpin_seq, mature_start, mature_length, arm)."""
    rows: list[tuple[str, str, int, int, str]] = []

    for record in re.split(r"^//$", text, flags=re.MULTILINE):
        record = record.strip()
        if not record:
            continue

        # Accession / locus name
        locus_m = re.search(r"^LOCUS\s+(\S+)", record, re.MULTILINE)
        if not locus_m:
            continue
        name = locus_m.group(1)

        # Sequence (ORIGIN section)
        origin_m = re.search(r"^ORIGIN\s*\n(.*)", record, re.MULTILINE | re.DOTALL)
        if not origin_m:
            continue
        seq = re.sub(r"[^a-zA-Z]", "", origin_m.group(1)).upper().replace("T", "U")
        if len(seq) < 40 or not all(c in VALID_NUCLEOTIDES for c in seq):
            continue

        # Mature miRNA features — stored as ncRNA with /ncRNA_class="miRNA"
        for mirna_m in re.finditer(
            r"^\s{5}ncRNA\s+(\S+)((?:\n\s{21}.*)*)",
            record,
            re.MULTILINE,
        ):
            loc_str = mirna_m.group(1)
            qualifiers = mirna_m.group(2)

            if 'ncRNA_class="miRNA"' not in qualifiers:
                continue

            product_m = re.search(r'/product="([^"]+)"', qualifiers)
            if not product_m:
                continue
            product = product_m.group(1)

            loc = _parse_location(loc_str)
            if loc is None:
                continue
            start, length = loc

            if not (0 <= start and start + length <= len(seq) and length >= 15):
                continue

            arm = "5p" if "5p" in product else "3p" if "3p" in product else "unk"
            rows.append((name, seq, start, length, arm))

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not GENBANK_CACHE.exists():
        ids = ncbi_search(
            "Homo sapiens[Organism] AND (miRNA[Title] OR microRNA[Title])"
            " AND 50:200[Sequence Length]",
            retmax=3000,
        )
        if not ids:
            raise RuntimeError("No sequences found. Check internet connection.")
        gb_text = ncbi_fetch_genbank(ids)
        GENBANK_CACHE.write_text(gb_text)
        print(f"GenBank data cached at {GENBANK_CACHE}")
    else:
        print(f"Using cached {GENBANK_CACHE}")
        gb_text = GENBANK_CACHE.read_text()

    print("Parsing GenBank records for mature miRNA features ...")
    rows = parse_genbank(gb_text)
    print(f"Extracted {len(rows)} hairpin–mature pairs")

    if len(rows) < 50:
        raise RuntimeError(
            "Too few miRNA feature annotations found. "
            "NCBI records may lack feature tables — try increasing retmax."
        )

    header = "hairpin_id,hairpin_sequence,mature_start,mature_length,arm"
    lines = [header]
    for hairpin_id, hairpin_seq, start, length, arm in rows:
        lines.append(f"{hairpin_id},{hairpin_seq},{start},{length},{arm}")
    DATASET_CSV.write_text("\n".join(lines) + "\n")
    print(f"Dataset saved to {DATASET_CSV}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
