"""
delete_index.py

Delete an entire OpenSearch index for MathMex.
Run from project root: python apps/opensearch/scripts/delete_index.py
"""
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(_BACKEND))

from opensearchpy import OpenSearch

from config_loader import get_config

config = get_config()
OPENSEARCH_HOST = config.get('opensearch', 'host')
USER = config.get('opensearch_admin', 'username')
PASSWORD = config.get('opensearch_admin', 'password')

# Name of the index to delete (change as needed)
INDEX_NAME = ''

# --- Connect ---
# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST}],
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
