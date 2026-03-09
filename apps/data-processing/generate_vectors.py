"""
generate_vectors.py

Generate vector embeddings from TSV for bulk indexing.
Reads from data/tsvs/, writes to data/vectors/.

Usage (from project root): python apps/data-processing/generate_vectors.py SOURCE TSV_FILE
  e.g. python processing/generate_vectors.py arxiv arxiv.tsv
"""
import argparse
import sys
import os
import csv
import tempfile
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(_BACKEND))

from dotenv import load_dotenv
load_dotenv()

from paths import ROOT, DATA_PATH, FORMULA_SEARCH_PATH, ENCODED_FILE_PATH, setup_formula_search_imports
from config_loader import get_config
from utils.format import format_for_tangent_cft_search

import numpy as np
import faiss
from tqdm import tqdm
import regex as re
import traceback
from sentence_transformers import SentenceTransformer

setup_formula_search_imports()
from tangent_cft_back_end import TangentCFTBackEnd
from Embedding_Preprocessing.encoder_tuple_level import TupleTokenizationMode

def write_temp_query_tsv(mathml_string: str):
    mathml_string = mathml_string.strip().strip('"').strip("'")
    tmp_tsv = tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False, newline="", encoding="utf-8")
    writer = csv.DictWriter(tmp_tsv, delimiter="\t", fieldnames=["id", "topic_id", "thread_id", "type", "formula"])
    writer.writeheader()
    writer.writerow({"id": "user_query", "topic_id": "A.000", "thread_id": "0000000", "type": "title", "formula": mathml_string})
    tmp_tsv.close()
    return tmp_tsv.name

fs = str(FORMULA_SEARCH_PATH)
backend = TangentCFTBackEnd(
    config_file=os.path.join(fs, "Configuration/config/config_1"),
    path_data_set=os.path.join(fs, "ARQMathDataset"),
    is_wiki=False,
    streaming=True,
    read_slt=True,
    queries_directory_path=str(ROOT / "ARQMathQueries" / "test_SLT.tsv"),
    faiss=True
)
backend.load_model(
    map_file_path=os.path.join(fs, "Embedding_Preprocessing/slt_encoder.tsv"),
    model_file_path=os.path.join(fs, "slt_model"),
    embedding_type=TupleTokenizationMode(3),
    ignore_full_relative_path=True,
    tokenize_all=False,
    tokenize_number=True
)
faiss_index = faiss.read_index(str(FORMULA_SEARCH_PATH / "slt_index.faiss"))

parser = argparse.ArgumentParser(description="Generate vector embeddings from TSV")
parser.add_argument("source", help="Source name (e.g. arxiv, wikipedia)")
parser.add_argument("tsv", help="TSV filename in data/tsvs/ (e.g. arxiv.tsv)")
args = parser.parse_args()

SOURCE = args.source
TSV_FILE = str(DATA_PATH / "tsvs" / args.tsv)
BATCH_SIZE = 5000

if not Path(TSV_FILE).exists():
    sys.exit(f"TSV file not found: {TSV_FILE}\nExpected: data/tsvs/{args.tsv}")

(DATA_PATH / "vectors").mkdir(parents=True, exist_ok=True)

config = get_config()
model = SentenceTransformer(os.path.expanduser(config.get("general", "model")))

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
                if not isinstance(vec, np.ndarray) or vec.size == 0:
                    continue
                vector_arr_formulas.append(vec)
                all_formulas_flat.append(formula)
                current_formula_pos += 1
                    # if len(batch) >= BATCH_SIZE:
                    #     np.save(f"{formula_batches_dir}/batch_{batch_count}.npy", np.array(batch, dtype=object))
                    #     batch = []
                    #     batch_count += 1
                
                # DELETE temp file to avoid /tmp filling up
                # try:
                #     os.remove(formula_file)
                # except Exception as e:
                #     print(f"Warning: failed to delete temp file {formula_file}: {e}")

            except Exception:
                continue
        formula_end = current_formula_pos
        formula_index.append((i, formula_start, formula_end))

    # if batch:  # batch not empty
    #     np.save(
    #         f"{formula_batches_dir}/batch_{batch_count}.npy",
    #         np.array(batch, dtype=object)
    #     )
    #     print(f"Saved final incomplete batch_{batch_count} with {len(batch)} items.")



np.save(str(DATA_PATH / f"vectors/{SOURCE}_text_vectors"), vector_arr_text)
print("Text vectors saved")
np.save(str(DATA_PATH / f"vectors/{SOURCE}_content_vectors"), vector_arr_body)
print("Body vectors saved")
np.save(str(DATA_PATH / f"vectors/{SOURCE}_formulas_vectors"), vector_arr_formulas)
print("Formula vectors saved")

# Save structured formula index
index_dtype = np.dtype([
    ("doc_id", np.int32),
    ("start", np.int64),
    ("end", np.int64)
])
index_array = np.array(formula_index, dtype=index_dtype)
np.save(str(DATA_PATH / f"vectors/{SOURCE}_formula_index.npy"), index_array)
print("Formula index saved", index_array.shape)

np.save(str(DATA_PATH / f"vectors/{SOURCE}_all_formulas_flat.npy"), all_formulas_flat)
print("All formula strings saved")


# batches = sorted(os.listdir(formula_batches_dir))
# arrays = [np.load(os.path.join(formula_batches_dir, f), allow_pickle=True) for f in batches]
# full = np.concatenate(arrays, axis=0)

# final = np.array(full, dtype=object)
# np.save(os.path.join(DATA_DIR, f"vectors/{SOURCE}_all_formulas_flat.npy"), final)


print("All vectors saved. Process complete.")
