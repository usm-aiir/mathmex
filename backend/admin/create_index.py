from opensearchpy import OpenSearch
from mappings import mapping
import json

# --- CONFIG ---
HOST = 'localhost'
PORT = 9200
USER = 'admin'
PASSWORD = 'Str0ngP0ssw0rd'
INDEX_NAME = 'mathmex'

# --- Connect ---
client = OpenSearch(
    hosts=[{'host': HOST, 'port': PORT}],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

# --- Create the index ---
if client.indices.exists(index=INDEX_NAME):
    print(f"Index '{INDEX_NAME}' already exists.")
else:
    response = client.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Created index '{INDEX_NAME}':")
    print(json.dumps(response, indent=2))
