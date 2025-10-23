"""
generate_jsonl.py

Script to generate a JSONL file for bulk indexing into OpenSearch.
Combines TSV metadata and NumPy vector embeddings into a single JSONL output.
"""
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import configparser
import numpy as np
import os
import csv
from tqdm import tqdm

# Change as needed: input TSV, NPY, and output JSONL file paths
TSV_FILE = ''
OUT_NPY_FILE = ''

# Load model to generate new embeddings
load_dotenv()
config = configparser.ConfigParser()
config.read( os.getenv("BACKEND_CONFIG") )
model = SentenceTransformer( config.get('general', 'model') )

# Global array
vector_arr = []

# Get total
with open(TSV_FILE, 'r', encoding='utf-8') as f_in:
    lines = f_in.readlines()

# Open TSV and output JSONL file
with open(TSV_FILE, 'r', encoding='utf-8') as f_in:
    reader = csv.reader(f_in, delimiter='\t')
    for i, row in tqdm( enumerate(reader), total=len(lines) ):
        if len(row) < 3:
            print(f"Skipping line {i} due to missing fields")
            continue

        vector_arr.append( model.encode( row[1] ) )


np.save(OUT_NPY_FILE, vector_arr)
print(f"Vectors saved to {OUT_NPY_FILE}")
