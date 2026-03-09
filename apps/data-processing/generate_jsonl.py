"""
generate_jsonl.py

Combine TSV metadata and vector embeddings into JSONL for bulk indexing.
Reads from data/tsvs/ and data/vectors/, writes to data/jsonl/.

Usage (from project root): python apps/data-processing/generate_jsonl.py SOURCE TSV_FILE
  e.g. python processing/generate_jsonl.py arxiv arxiv.tsv

Run generate_vectors.py first to create the vector files.
"""
import argparse
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(_BACKEND))

from paths import DATA_PATH

import numpy as np
import csv
import json
from tqdm import tqdm

MEDIA_TYPE = {
    "arxiv": "pdf",
    "mathematica": "article",
    "math-overflow": "article",
    "math-stack-exchange": "article",
    "wikipedia": "article",
    "youtube": "video",
}

parser = argparse.ArgumentParser(description="Combine TSV + vectors into JSONL for bulk indexing")
parser.add_argument("source", help="Source name (e.g. arxiv, wikipedia)")
parser.add_argument("tsv", help="TSV filename in data/tsvs/ (e.g. arxiv.tsv)")
args = parser.parse_args()

SOURCE = args.source
TSV_FILE = str(DATA_PATH / "tsvs" / args.tsv)
FULL_VECTS = str(DATA_PATH / f"vectors/{SOURCE}_content_vectors.npy")
TEXT_VECTS = str(DATA_PATH / f"vectors/{SOURCE}_text_vectors.npy")
FORMULA_VECTS = str(DATA_PATH / f"vectors/{SOURCE}_formulas_vectors.npy")
FORMULA_VECT_INDEX = str(DATA_PATH / f"vectors/{SOURCE}_formula_index.npy")
FORMULA_LATEX = str(DATA_PATH / f"vectors/{SOURCE}_all_formulas_flat.npy")
OUT_JSONL_FILE = str(DATA_PATH / f"jsonl/mathmex_{SOURCE}.jsonl")

for p in [TSV_FILE, FULL_VECTS, TEXT_VECTS, FORMULA_VECTS, FORMULA_VECT_INDEX, FORMULA_LATEX]:
    if not Path(p).exists():
        sys.exit(f"File not found: {p}\nRun generate_vectors.py first.")

Path(OUT_JSONL_FILE).parent.mkdir(parents=True, exist_ok=True)

# Load vector embeddings from .npy file
body_vecs = np.load(FULL_VECTS)
print(f"Loaded embeddings of content shape: {body_vecs.shape}")
text_vecs = np.load(TEXT_VECTS)
print(f"Loaded embeddings of text shape: {text_vecs.shape}")
formula_vecs = np.load(FORMULA_VECTS, allow_pickle=True)
print(f"Loaded embeddings of formulas shape: {formula_vecs.shape}")

formula_index = np.load(FORMULA_VECT_INDEX, allow_pickle=True)

formula_index_map = {row["doc_id"]: (int(row["start"]), int(row["end"])) for row in formula_index}

all_formulas_flat = np.load(FORMULA_LATEX, allow_pickle=True)



# Open TSV and output JSONL file
with open(TSV_FILE, 'r', encoding='utf-8') as f_in, \
        open(OUT_JSONL_FILE, 'w', encoding='utf-8') as f_out:
    reader = csv.reader(f_in, delimiter='\t')
    for i, row in tqdm(enumerate(reader), total=body_vecs.shape[0]):
        if len(row) < 3:
            print(f"Skipping line {i} due to missing fields")
            continue
        
        # Get formula vector slice for this document
        start, end = formula_index_map.get(i, (0, 0))
        doc_formula_vecs = formula_vecs[start:end] if end > start else []

        # Get corresponding LaTeX strings
        doc_formulas_latex = all_formulas_flat[start:end] if end > start else []

        # Combine into nested structure for OpenSearch
        doc_formulas = [
            {"latex": latex, "formula_vector": vec.tolist()}
            for latex, vec in zip(doc_formulas_latex, doc_formula_vecs)
        ]

        obj = {
            "doc_ID": f"doc_{i}",
            "title": row[0],
            "media_type": MEDIA_TYPE.get(SOURCE, "article"),
            "body_text": row[1],
            "body_vector": body_vecs[i].tolist(),
            "text_vector": text_vecs[i].tolist(),
            "formulas": doc_formulas, # nested list with latex + vector
            "link": row[2],
        }
        # Write each object as a line in the JSONL file
        f_out.write(json.dumps(obj) + '\n')

print(f"Combined file saved to {OUT_JSONL_FILE}")

