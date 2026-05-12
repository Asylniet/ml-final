import json
import pathlib
import random
import time
import urllib.parse
import urllib.request
from collections import defaultdict

DATA_DIR = pathlib.Path(__file__).parent.parent / "src" / "data"
HAIRPIN_FA = DATA_DIR / "hairpin.fa"
DATASET_CSV = DATA_DIR / "dataset.csv"

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
VALID_NUCLEOTIDES = set("AUGC")
BATCH_SIZE = 200


def ncbi_search(term: str, db: str = "nuccore", retmax: int = 3000) -> list[str]:
    params = urllib.parse.urlencode({
        "db": db,
        "term": term,
        "retmax": retmax,
        "retmode": "json",
    })
    url = f"{NCBI_BASE}/esearch.fcgi?{params}"
    print(f"Searching NCBI: {term!r} ...")
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    ids = data["esearchresult"]["idlist"]
    print(f"Found {len(ids)} entries")
    return ids


def ncbi_fetch_fasta(ids: list[str], db: str = "nuccore") -> str:
    chunks = [ids[i : i + BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)]
    all_fasta = []
    for n, chunk in enumerate(chunks, 1):
        print(f"  Fetching batch {n}/{len(chunks)} ({len(chunk)} sequences)...")
        params = urllib.parse.urlencode({
            "db": db,
            "id": ",".join(chunk),
            "rettype": "fasta",
            "retmode": "text",
        })
        url = f"{NCBI_BASE}/efetch.fcgi?{params}"
        with urllib.request.urlopen(url) as resp:
            all_fasta.append(resp.read().decode("utf-8"))
        time.sleep(0.4)  # NCBI rate limit: max 3 req/s without API key
    return "\n".join(all_fasta)


def parse_fasta(text: str) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    name, seq_parts = "", []
    for line in text.splitlines():
        if line.startswith(">"):
            if name and seq_parts:
                records.append((name, "".join(seq_parts).upper()))
            name = line[1:].split()[0]
            seq_parts = []
        else:
            seq_parts.append(line.strip())
    if name and seq_parts:
        records.append((name, "".join(seq_parts).upper()))
    return records


def clean_sequences(records: list[tuple[str, str]]) -> list[str]:
    seen: set[str] = set()
    seqs: list[str] = []
    for _, seq in records:
        clean = seq.replace("T", "U")
        if (
            40 <= len(clean) <= 250
            and all(c in VALID_NUCLEOTIDES for c in clean)
            and clean not in seen
        ):
            seen.add(clean)
            seqs.append(clean)
    return seqs


def dinucleotide_shuffle(seq: str, seed: int = 0) -> str:
    """Shuffle preserving dinucleotide frequencies (Altschul-Erickson algorithm)."""
    rng = random.Random(seed)
    edges: dict[str, list[str]] = defaultdict(list)
    for i in range(len(seq) - 1):
        edges[seq[i]].append(seq[i + 1])
    for nt in edges:
        rng.shuffle(edges[nt])
    last = seq[-1]
    path = [last]
    stack = [seq[0]]
    while stack:
        v = stack[-1]
        if edges[v]:
            stack.append(edges[v].pop())
        else:
            path.append(stack.pop())
    shuffled = "".join(reversed(path))
    if len(shuffled) != len(seq):
        shuffled_list = list(seq)
        rng.shuffle(shuffled_list)
        shuffled = "".join(shuffled_list)
    return shuffled


def _hard_negatives(lengths: list[int], rng: random.Random) -> list[str]:
    """Generate biologically implausible sequences the model must learn to reject."""
    nucleotides = ["A", "U", "G", "C"]
    seqs: list[str] = []

    # Poly-nucleotide (all-A, all-U, all-G, all-C)
    for nt in nucleotides:
        for length in rng.sample(lengths, k=min(4, len(lengths))):
            seqs.append(nt * length)

    # Low-complexity repeats (e.g. AAAUUU..., AUGAUG...)
    motifs = ["AAAU", "UUUG", "AAGG", "UCUC", "GAUC", "AUAU"]
    for motif in motifs:
        for length in rng.sample(lengths, k=min(3, len(lengths))):
            seqs.append((motif * (length // len(motif) + 1))[:length])

    # Uniformly random sequences (no biological bias)
    for length in lengths[: len(lengths) // 2]:
        seqs.append("".join(rng.choices(nucleotides, k=length)))

    return seqs


def build_dataset(positive_seqs: list[str]) -> list[tuple[str, int]]:
    dataset: list[tuple[str, int]] = [(seq, 1) for seq in positive_seqs]

    # Shuffled negatives (same composition, different order)
    for i, seq in enumerate(positive_seqs):
        dataset.append((dinucleotide_shuffle(seq, seed=i), 0))

    # Hard negatives (extreme cases no miRNA classifier should misclassify)
    lengths = [len(s) for s in positive_seqs]
    hard = _hard_negatives(lengths, rng=random.Random(0))
    for seq in hard:
        dataset.append((seq, 0))

    random.shuffle(dataset)
    return dataset


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not HAIRPIN_FA.exists():
        # Search NCBI nuccore for human pre-miRNA sequences (50–200 nt)
        ids = ncbi_search(
            "Homo sapiens[Organism] AND (miRNA[Title] OR microRNA[Title]) AND 50:200[Sequence Length]",
            retmax=2000,
        )
        if not ids:
            raise RuntimeError("No sequences found. Check your internet connection.")
        fasta_text = ncbi_fetch_fasta(ids)
        _ = HAIRPIN_FA.write_text(fasta_text)
        print(f"Sequences saved to {HAIRPIN_FA}")
    else:
        print(f"Using cached {HAIRPIN_FA}")

    records = parse_fasta(HAIRPIN_FA.read_text())
    positive_seqs = clean_sequences(records)
    print(f"Valid human pre-miRNA sequences: {len(positive_seqs)}")

    if len(positive_seqs) < 10:
        raise RuntimeError("Too few sequences. The download may have failed.")

    dataset = build_dataset(positive_seqs)

    lines = ["sequence,label"]
    for seq, label in dataset:
        lines.append(f"{seq},{label}")
    _ = DATASET_CSV.write_text("\n".join(lines) + "\n")
    print(f"Dataset saved to {DATASET_CSV}  ({len(dataset)} samples, balanced)")


if __name__ == "__main__":
    main()
