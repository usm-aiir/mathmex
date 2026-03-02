import numpy as np
import faiss # Use faiss-gpu for this script
import json
import os
import csv
import configparser
from tqdm import tqdm
from opensearchpy import OpenSearch, helpers

config = configparser.ConfigParser()
config.read('../backend/config.ini')

client = OpenSearch(
    hosts=[{'host': config.get('opensearch', 'host'), 'port': 443}],
    http_auth=(config.get('admin', 'user'), config.get('admin', 'password')),
    use_ssl=True, verify_certs=False, ssl_show_warn=False
)

K_NEIGHBORS = 6       # 1 for the document itself + 5 branches
THRESHOLD = 0.75      # Minimum cosine similarity to draw an edge
CHUNK_SIZE = 10000    # How many vectors to process at once

print("Initializing GPU resources...")
res = faiss.StandardGpuResources()

def generate_bulk_updates(file_path):
    """Reads the JSONL file line-by-line and yields actions for OpenSearch."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line)

# Dynamically Find All MathMex Indices
print("Querying OpenSearch for matching indices...")
matching_indices = list(client.indices.get(index='mathmex_*').keys())
print(f"Found {len(matching_indices)} indices: {matching_indices}\n")

# Build Global Registry
global_id_map = []
corpus_registry = []
global_offset = 0
vector_dim = 0

print(f"{'='*50}\nPHASE 1: Building Global ID Map\n{'='*50}")

for index_name in matching_indices:
    source = index_name.replace("mathmex_", "")
    if source == "math-stack-exchange":
        source = "mse"

    vector_file = f'../backend/data/vectors/{source}_content_vectors.npy'
    
    if not os.path.exists(vector_file):
        print(f"  [WARNING] Vector file not found at {vector_file}. Skipping {source}...\n")
        continue

    body_vecs = np.load(vector_file, mmap_mode='r')
    total_docs, current_dim = body_vecs.shape
    vector_dim = current_dim

    local_map = [None] * total_docs

    # Build the ID Map for this Index
    print(f"  [1] Scanning OpenSearch to map IDs for {index_name}...")
    query = {"query": {"match_all": {}}, "_source": ["doc_ID"]}
    
    # size=100 added to prevent OpenSearch circuit breaker errors
    for doc in helpers.scan(client, index=index_name, query=query, size=100):
        internal_doc_id = doc['_source'].get('doc_ID')
        if internal_doc_id and internal_doc_id.startswith('doc_'):
            try:
                idx = int(internal_doc_id.split('_')[1])
                if idx < total_docs:
                    local_map[idx] = {"_index": index_name, "_id": doc['_id']}
            except ValueError:
                continue
                
    global_id_map.extend(local_map)
    corpus_registry.append({
        "source": source,
        "index_name": index_name,
        "vector_file": vector_file,
        "num_docs": total_docs,
        "offset": global_offset
    })
    global_offset += total_docs

# Global FAISS Injection
print(f"\n{'='*50}\nPHASE 2: Building Global FAISS Index (Device 1)\n{'='*50}")

# Create CPU index and instantly transfer it to GPU 1
cpu_index = faiss.IndexFlatIP(vector_dim)
gpu_index = faiss.index_cpu_to_gpu(res, 1, cpu_index)

# Load Vectors and Build FAISS Index
for corpus in corpus_registry:
    body_vecs = np.load(corpus["vector_file"], mmap_mode='r')
    for i in tqdm(range(0, corpus["num_docs"], CHUNK_SIZE), desc=f"  Indexing {corpus['source']} to GPU"):
        chunk = np.array(body_vecs[i:i+CHUNK_SIZE], dtype='float32')
        faiss.normalize_L2(chunk)
        gpu_index.add(chunk)

# Cross-Index Querying & Output
print(f"\n{'='*50}\nPHASE 3: Calculating Global Edges & Uploading\n{'='*50}")

# Process Each Index Sequentially
for corpus in corpus_registry:
    source = corpus["source"]
    index_name = corpus["index_name"]
    global_offset = corpus["offset"]

    # If completing graphs in parts, put the already completed indices here to skip
    # completed = ["arxiv", "mse", "mse-proofs", "mathematica", "math-overflow"]
    # if source in completed:
    #     continue

    out_update_file = f'../backend/data/jsonl/{source}_global_graph_updates.jsonl'
    out_tsv_graph = f'../backend/data/graphs/{source}_global_edge_list.tsv'
    
    print(f"{'='*50}")
    print(f"Starting GPU pipeline for: {source.upper()} (Index: {index_name})")
    print(f"{'='*50}")

    os.makedirs(os.path.dirname(out_update_file), exist_ok=True)
    os.makedirs(os.path.dirname(out_tsv_graph), exist_ok=True)

    body_vecs = np.load(corpus["vector_file"], mmap_mode='r')

    # Calculate Edges and Write to Disk (JSONL & CSV)
    print(f"\n  [3] Calculating edges and saving backups to disk...")
    
    with open(out_update_file, 'w', encoding='utf-8') as f_out_jsonl, \
         open(out_tsv_graph, 'w', newline='', encoding='utf-8') as f_out_tsv:
        
        # Initialize TSV writer for the static graph backup
        tsv_writer = csv.writer(f_out_tsv, delimiter='\t')
        tsv_writer.writerow(['source_index', 'source_id', 'target_index', 'target_id', 'weight'])
        
        for i in tqdm(range(0, corpus["num_docs"], CHUNK_SIZE), desc=f"  Querying {source}"):
            query_chunk = np.array(body_vecs[i:i+CHUNK_SIZE], dtype='float32')
            faiss.normalize_L2(query_chunk)
            
            distances, indices = gpu_index.search(query_chunk, K_NEIGHBORS)
            
            for j in range(len(query_chunk)):
                local_idx = i + j
                current_global_idx = global_offset + local_idx
                
                current_doc_info = global_id_map[current_global_idx]
                if not current_doc_info:
                    continue # Skip if we can't map the source document
                
                branches = []
                
                for rank in range(1, K_NEIGHBORS):
                    score = distances[j][rank]
                    neighbor_global_idx = indices[j][rank]
                    
                    if score >= THRESHOLD and neighbor_global_idx != current_global_idx:
                        neighbor_info = global_id_map[neighbor_global_idx]
                        
                        if neighbor_info:
                            branches.append(neighbor_info)
                            # Write the explicit edge to TSV backup
                            tsv_writer.writerow([
                                current_doc_info["_index"], current_doc_info["_id"],
                                neighbor_info["_index"], neighbor_info["_id"],
                                round(float(score), 4)
                            ])
                
                # If valid branches, prepare the OpenSearch update
                if branches:
                    action_dict = {
                        "_op_type": "update",
                        "_index": current_doc_info["_index"],
                        "_id": current_doc_info["_id"],
                        "doc": {"global_topics": branches} # Changed to preserve existing edges
                    }
                    f_out_jsonl.write(json.dumps(action_dict) + '\n')

    # Execute the Bulk Update to OpenSearch
    print(f"\n  [4] Pushing updates directly to OpenSearch...")
    try:
        success_count, errors = helpers.bulk(
            client, 
            generate_bulk_updates(out_update_file), 
            chunk_size=1000, 
            request_timeout=120
        )
        print(f"  Successfully updated {success_count} documents in {index_name}.")
        if errors:
            print(f"  [WARNING] Failed to update {len(errors)} documents.")
    except Exception as e:
        print(f"  [ERROR] Bulk upload failed for {source}: {e}")

    print(f"  Finished processing {source}.\n")

print("All MathMex indices processed successfully.")