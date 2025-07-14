"""
delete_index.py

Script to delete an entire OpenSearch index for MathMex.
Run this script to remove an index and all its data from OpenSearch.
"""
from opensearchpy import OpenSearch

# --- CONFIG ---
# OpenSearch connection settings
HOST = 'localhost'
PORT = 9200
USER = 'admin'
PASSWORD = 'Str0ngP0ssw0rd'
# Name of the index to delete (change as needed)
INDEX_NAME = 'mathmex_math-stack-exchange'

# --- Connect ---
# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': HOST, 'port': PORT}],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

# --- Delete the entire index ---
# Check if the index exists before attempting to delete
if client.indices.exists(index=INDEX_NAME):
    client.indices.delete(index=INDEX_NAME)
    print(f"Deleted index '{INDEX_NAME}'.")
else:
    print(f"Index '{INDEX_NAME}' does not exist.")
