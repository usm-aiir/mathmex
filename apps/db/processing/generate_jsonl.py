"""
generate_jsonl.py

Script to generate a JSONL file for bulk indexing into OpenSearch.
Combines TSV metadata and NumPy vector embeddings into a single JSONL output.
"""
import os
import numpy as np
import csv
import json
from tqdm import tqdm

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../../../data'))

# Unused dict
# Use this as reference for the 'media_type' property
media_type = {
    "arxiv" : "pdf",
    "mathematica" : "article",
    "math-overflow" : "article",
    "math-stack-exchange" : "article",
    "wikipedia" : "article",
    "youtube" : "video"
}

SOURCE = ''

# Change as needed: input TSV, NPY, and output JSONL file paths
TSV_FILE = os.path.join(DATA_DIR, 'tsvs/arxiv.tsv')
FULL_VECTS = os.path.join(DATA_DIR, f'vectors/{SOURCE}_content_vectors.npy')
TEXT_VECTS = os.path.join(DATA_DIR, f'vectors/{SOURCE}_text_vectors.npy')
FORMULA_VECTS = os.path.join(DATA_DIR, f'vectors/{SOURCE}_formulas_vectors.npy')
FORMULA_VECT_INDEX = os.path.join(DATA_DIR, f'vectors/{SOURCE}_formula_index.npy')
FORMULA_LATEX = os.path.join(DATA_DIR, f'vectors/{SOURCE}_all_formulas_flat.npy')
OUT_JSONL_FILE = os.path.join(DATA_DIR, f'jsonl/mathmex_{SOURCE}.jsonl')

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
            "doc_ID":f"doc_{i}",
            "title": row[0],

            # Change this depending on what type of data you are generating a *.jsonl for
            "media_type": "pdf",

            "body_text": row[1],
            "body_vector": body_vecs[i].tolist(),
            "text_vector": text_vecs[i].tolist(),
            "formulas": doc_formulas, # nested list with latex + vector
            "link": row[2],
        }
        # Write each object as a line in the JSONL file
        f_out.write(json.dumps(obj) + '\n')

print(f"Combined file saved to {OUT_JSONL_FILE}")

