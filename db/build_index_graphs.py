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

# Process Each Index Sequentially
for index_name in matching_indices:
    source = index_name.replace("mathmex_", "")

    if source == "math-stack-exchange":
        source = "mse"


    # If completing graphs in parts, put the already completed indices here to skip
    # completed = ["arxiv", "mse", "mse-proofs", "mathematica", "math-overflow"]
    # if source in completed:
    #     continue
    
    # ../backend/data/vectors/{source}_content_vectors.npy
    vector_file = f'../backend/data/vectors/{source}_content_vectors.npy'
    out_update_file = f'../backend/data/jsonl/{source}_graph_updates.jsonl'
    out_tsv_graph = f'../backend/data/graphs/{source}_edge_list.tsv'
    
    print(f"{'='*50}")
    print(f"Starting GPU pipeline for: {source.upper()} (Index: {index_name})")
    print(f"{'='*50}")

    if not os.path.exists(vector_file):
        print(f"  [WARNING] Vector file not found at {vector_file}. Skipping {source}...\n")
        continue

    # Build the ID Map for this Index
    print(f"  [1] Scanning OpenSearch to map IDs for {index_name}...")
    id_mapping = {}
    query = {"query": {"match_all": {}}, "_source": ["doc_ID"]}
    
    for doc in helpers.scan(client, index=index_name, query=query):
        internal_doc_id = doc['_source'].get('doc_ID')
        if internal_doc_id:
            id_mapping[internal_doc_id] = doc['_id']
            
    print(f"  Mapped {len(id_mapping)} documents.\n")

    # Load Vectors and Build FAISS Index
    print(f"  [2] Loading vectors and building FAISS index...")
    body_vecs = np.load(vector_file, mmap_mode='r')
    total_docs, vector_dim = body_vecs.shape

    # Create CPU index and instantly transfer it to GPU 1
    cpu_index = faiss.IndexFlatIP(vector_dim)
    gpu_index = faiss.index_cpu_to_gpu(res, 1, cpu_index)
    
    for i in tqdm(range(0, total_docs, CHUNK_SIZE), desc=f"  Indexing {source} to GPU"):
        chunk = np.array(body_vecs[i:i+CHUNK_SIZE], dtype='float32')
        faiss.normalize_L2(chunk)
        gpu_index.add(chunk)

    # Calculate Edges and Write to Disk (JSONL & CSV)
    print(f"\n  [3] Calculating edges and saving backups to disk...")
    
    with open(out_update_file, 'w', encoding='utf-8') as f_out_jsonl, \
         open(out_tsv_graph, 'w', newline='', encoding='utf-8') as f_out_tsv:
        
        # Initialize TSV writer for the static graph backup
        tsv_writer = csv.writer(f_out_tsv, delimiter='\t')
        tsv_writer.writerow(['source_node', 'target_node', 'weight'])
        
        for i in tqdm(range(0, total_docs, CHUNK_SIZE), desc=f"  Querying {source}"):
            query_chunk = np.array(body_vecs[i:i+CHUNK_SIZE], dtype='float32')
            faiss.normalize_L2(query_chunk)
            
            distances, indices = gpu_index.search(query_chunk, K_NEIGHBORS)
            
            for j in range(len(query_chunk)):
                current_doc_idx = i + j
                current_internal_id = f"doc_{current_doc_idx}"
                real_current_id = id_mapping.get(current_internal_id)
                
                if not real_current_id:
                    continue # Skip if we can't map the source document
                
                branches = []
                
                for rank in range(1, K_NEIGHBORS):
                    score = distances[j][rank]
                    neighbor_idx = indices[j][rank]
                    
                    if score >= THRESHOLD and neighbor_idx != current_doc_idx:
                        neighbor_internal_id = f"doc_{neighbor_idx}"
                        real_neighbor_id = id_mapping.get(neighbor_internal_id)
                        
                        if real_neighbor_id:
                            branches.append(real_neighbor_id)
                            # Write the explicit edge to TSV backup
                            tsv_writer.writerow([real_current_id, real_neighbor_id, round(float(score), 4)])
                
                # If valid branches, prepare the OpenSearch update
                if branches:
                    action_dict = {
                        "_op_type": "update",
                        "_index": index_name,
                        "_id": real_current_id,
                        "doc": {"relevant_topics": branches}
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