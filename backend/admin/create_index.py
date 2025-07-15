"""
create_index.py

Script to create an OpenSearch index for MathMex with the specified mapping.
Run this script to initialize a new index before bulk uploading documents.
"""
from opensearchpy import OpenSearch
from mappings import mapping
import json
import configparser

# --- Load Configuration from config.ini ---
config = configparser.ConfigParser()
config.read('../config.ini')

# OpenSearch Client Configuration from file
HOST = config.get('opensearch', 'host')
PORT = config.getint('opensearch', 'port') # Use getint for numbers
USER = config.get('opensearch', 'admin_user')
PASSWORD = config.get('opensearch', 'admin_password')

# Name of the index to create (change as needed)
INDEX_NAME = 'mathmex_wikipedia'

# --- Connect ---
# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': HOST, 'port': PORT}],
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
