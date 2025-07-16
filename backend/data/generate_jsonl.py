"""
generate_jsonl.py

Script to generate a JSONL file for bulk indexing into OpenSearch.
Combines TSV metadata and NumPy vector embeddings into a single JSONL output.
"""
import numpy as np
import csv
import json
from tqdm import tqdm

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

# Change as needed: input TSV, NPY, and output JSONL file paths
TSV_FILE = 'tsvs/'
NPY_FILE = 'vectors/'
OUT_JSONL_FILE = 'jsonl/'

# Load vector embeddings from .npy file
embeddings = np.load(NPY_FILE)
print(f"Loaded embeddings of shape: {embeddings.shape}")

# Open TSV and output JSONL file
with open(TSV_FILE, 'r', encoding='utf-8') as f_in, \
        open(OUT_JSONL_FILE, 'w', encoding='utf-8') as f_out:
    reader = csv.reader(f_in, delimiter='\t')
    for i, row in tqdm(enumerate(reader), total=embeddings.shape[0]):
        if len(row) < 3:
            print(f"Skipping line {i} due to missing fields")
            continue
        obj = {
            "title": row[0],

            # Change this depending on what type of data you are generating a *.jsonl for
            "media_type": "video",

            "body_text": row[1],
            "body_vector": embeddings[i].tolist(),
            "link": row[2],
        }
        # Write each object as a line in the JSONL file
        f_out.write(json.dumps(obj) + '\n')

print(f"Combined file saved to {OUT_JSONL_FILE}")
