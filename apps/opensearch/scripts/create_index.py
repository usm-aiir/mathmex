"""
create_index.py

Create an OpenSearch index for MathMex with the specified mapping.
Run from project root: python apps/opensearch/scripts/create_index.py
"""
import sys
from pathlib import Path

_OPENSEARCH = Path(__file__).resolve().parents[1]
_BACKEND = _OPENSEARCH.parent / "backend"
sys.path.insert(0, str(_OPENSEARCH))
sys.path.insert(0, str(_BACKEND))

from opensearchpy import OpenSearch
from schemas.mappings import mapping
import json

from config_loader import get_config

config = get_config()
OPENSEARCH_HOST = config.get('opensearch', 'host')
USER = config.get('opensearch_admin', 'username')
PASSWORD = config.get('opensearch_admin', 'password')

# Name of the index to create (change as needed)
INDEX_NAME = 'mathmex_youtube'

# --- Connect ---
# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST}],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

# --- Create the index ---
# Check if the index already exists
if client.indices.exists(index=INDEX_NAME):
    print(f"Index '{INDEX_NAME}' already exists.")
else:
    # Create the index with the provided mapping
    response = client.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Created index '{INDEX_NAME}':")
    print(json.dumps(response, indent=2))