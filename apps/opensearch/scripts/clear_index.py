"""
clear_index.py

Clear all documents from OpenSearch indices (keeps index structure).
Run from project root: python apps/opensearch/scripts/clear_index.py
"""
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(_BACKEND))

from opensearchpy import OpenSearch, ConnectionTimeout

from config_loader import get_config

config = get_config()
OPENSEARCH_HOST = config.get('opensearch', 'host')
USER = config.get('opensearch_admin', 'username')
PASSWORD = config.get('opensearch_admin', 'password')

# Name or pattern of the index to clear (wildcards allowed)
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
