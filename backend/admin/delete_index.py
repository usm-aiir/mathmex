"""
delete_index.py

Script to delete an entire OpenSearch index for MathMex.
Run this script to remove an index and all its data from OpenSearch.
"""
from opensearchpy import OpenSearch
import configparser

# --- Load Configuration from config.ini ---
config = configparser.ConfigParser()
config.read('../config.ini')

# OpenSearch Client Configuration from file
HOST = config.get('opensearch', 'host')
PORT = config.getint('opensearch', 'port') # Use getint for numbers
USER = config.get('opensearch', 'admin_user')
PASSWORD = config.get('opensearch', 'admin_password')
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
