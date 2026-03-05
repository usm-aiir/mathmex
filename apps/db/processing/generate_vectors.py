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
import regex as re
import sys
import traceback
import glob

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../backend"))
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../data"))
FORMULA_SEARCH_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../formula-search"))

sys.path.extend([BACKEND_DIR, FORMULA_SEARCH_DIR])

from app import faiss_index, backend, write_temp_query_tsv
from utils.format import format_for_tangent_cft_search
from tangent_cft_back_end import TangentCFTBackEnd
from Embedding_Preprocessing.encoder_tuple_level import TupleTokenizationMode


ENCODED_FILE_PATH = os.path.join(DATA_DIR, "jsonl/TangentCFT/encoded.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "jsonl/TangentCFT/encoded_index.json")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "jsonl/TangentCFT/slt_index.faiss")

# # Change as needed: input TSV, NPY, and output JSONL file paths
TSV_FILE = ''
SOURCE = ''

# Flush results to disk between batches (for arXiv)
BATCH_SIZE = 5000

# Load model to generate new embeddings
load_dotenv()
config = configparser.ConfigParser()
config.read( os.getenv("BACKEND_CONFIG") )
model = SentenceTransformer( config.get('general', 'model') )

# Global array
vector_arr = []
vector_arr_body = []
vector_arr_text = []
vector_arr_formulas = []
all_formulas_flat = []
batch = []

# batch_count = 0
# formula_batches_dir = f"./data/{SOURCE}_latex_batches"
# os.makedirs(formula_batches_dir, exist_ok=True)

# Track start/end index for formulas of each doc
formula_index = []   # list of (doc_id, start, end)
current_formula_pos = 0

# Get total
with open(TSV_FILE, 'r', encoding='utf-8') as f_in:
    lines = f_in.readlines()

# Open TSV and output JSONL file
with open(TSV_FILE, 'r', encoding='utf-8') as f_in:
    reader = csv.reader(f_in, delimiter='\t')

    # Regex to match LaTeX formulas in common delimiters
    latex_pattern = re.compile(
        r'(\$(?:[^$]|\\\$)+\$)|'       # $...$
        r'(\\\((?:[^)]|\\\))+\\\))|'   # \(...\)
        r'(\\\[(?:[^\]]|\\\])+\\\])'   # \[...\]
    )
    for i, row in tqdm( enumerate(reader), total=len(lines) ):
        if len(row) < 3:
            print(f"Skipping line {i} due to missing fields")
            continue

        vector_arr.append( model.encode( row[1] ) )


        title, body, source_url = row[0].strip(), row[1].strip(), row[2].strip()

        matches = latex_pattern.findall(body)
        formulas = []
        formula_start = current_formula_pos
        for group in matches:
            formula = next((g for g in group if g), None)
            if formula:
                formulas.append(formula.strip())
        
        text_only = latex_pattern.sub('', body).strip()

        entry = {
            "title": title,
            "url": source_url,
            "body": body,
            "body_text": text_only,
            "formulas": formulas
        }
        vector_arr_body.append(model.encode(body))
        vector_arr_text.append(model.encode(text_only))
        for formula in formulas:
            try:
                formula_ml = format_for_tangent_cft_search(formula)

                formula_file = write_temp_query_tsv(formula_ml)

                backend.data_reader.queries_dir_path = formula_file

                vec = backend.retrieval(
                    encoded_file_path=ENCODED_FILE_PATH,
                    embedding_type=TupleTokenizationMode(3),
                    ignore_full_relative_path=True,
                    tokenize_all=False,
                    tokenize_number=True,
                    streaming=True,
                    faiss=True,
                    faiss_index=faiss_index,
                    single_query=True,
                    do_retrieval=False
                )
                if vec.size == 0:
                    print(f"Skipping formula '{formula}' due to empty tuples") 
                    continue
                else:
                    vector_arr_formulas.append(vec)
                    # all_formulas_flat.append(formula)  # only if vector exists
                    # batch.append(formula)
                    # current_formula_pos += 1
                    # if len(batch) >= BATCH_SIZE:
                    #     np.save(f"{formula_batches_dir}/batch_{batch_count}.npy", np.array(batch, dtype=object))
                    #     batch = []
                    #     batch_count += 1
                
                # DELETE temp file to avoid /tmp filling up
                # try:
                #     os.remove(formula_file)
                # except Exception as e:
                #     print(f"Warning: failed to delete temp file {formula_file}: {e}")

            except Exception as e:
                print(f"Error encoding formula '{formula}': {e}")
                traceback.print_exc
                continue
        formula_end = current_formula_pos
        formula_index.append((i, formula_start, formula_end))

    # if batch:  # batch not empty
    #     np.save(
    #         f"{formula_batches_dir}/batch_{batch_count}.npy",
    #         np.array(batch, dtype=object)
    #     )
    #     print(f"Saved final incomplete batch_{batch_count} with {len(batch)} items.")



np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_text_vectors"), vector_arr_text)
print("Text vectors saved")
np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_content_vectors"), vector_arr_body)
print("Body vectors saved")
np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_formulas_vectors"), vector_arr_formulas)
print("Formula vectors saved")

# Save structured formula index
index_dtype = np.dtype([
    ("doc_id", np.int32),
    ("start", np.int64),
    ("end", np.int64)
])
index_array = np.array(formula_index, dtype=index_dtype)
np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_formula_index.npy"), index_array)
print("Formula index saved", index_array.shape)

np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_all_formulas_flat.npy"), all_formulas_flat)
print("All formula strings saved")


# batches = sorted(os.listdir(formula_batches_dir))
# arrays = [np.load(os.path.join(formula_batches_dir, f), allow_pickle=True) for f in batches]
# full = np.concatenate(arrays, axis=0)

# final = np.array(full, dtype=object)
# np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_all_formulas_flat.npy"), final)


print("All vectors saved. Process complete.")

vectors = np.load(os.path.join(DATA_DIR, f"vectors/{SOURCE}_formulas_vectors.npy"), allow_pickle=True)
print("Formula Vector array shape:", vectors.shape)

vectors = np.load(os.path.join(DATA_DIR, f"vectors/{SOURCE}_content_vectors.npy"), allow_pickle=True)
print("Content Vector array shape:", vectors.shape)

vectors = np.load(os.path.join(DATA_DIR, f"vectors/{SOURCE}_text_vectors.npy"), allow_pickle=True)
print("Text Vector array shape:", vectors.shape)

all_formulas_flat = np.load(os.path.join(DATA_DIR, f"vectors/{SOURCE}_all_formulas_flat.npy"), allow_pickle=True)
print(f"Loaded {len(all_formulas_flat)} formulas")
print("First 10 formulas:", all_formulas_flat[:10])
