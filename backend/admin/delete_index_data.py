"""
delete_index_data.py

Script to delete all documents from one or more OpenSearch indices for MathMex.
Run this script to clear all data from the specified index or indices, but keep the index structure.
"""
from opensearchpy import OpenSearch, ConnectionTimeout

# --- CONFIG ---
# OpenSearch connection settings
HOST = 'localhost'
PORT = 9200
USER = 'admin'
PASSWORD = 'Str0ngP0ssw0rd'
# Name or pattern of the index to clear (wildcards allowed)
INDEX_NAME = 'mathmex*'

# --- Connect ---
# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': HOST, 'port': PORT}],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

try:
    # --- Delete all documents ---
    # Use delete_by_query to remove all documents from the index (but keep the index itself)
    response = client.delete_by_query(
        index=INDEX_NAME,
        body={
            "query": {
                "match_all": {}
            }
        }
    )
except ConnectionTimeout as e:
    print(f"Deleted documents from index '{INDEX_NAME}':")
