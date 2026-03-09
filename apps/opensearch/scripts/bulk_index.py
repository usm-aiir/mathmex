"""
bulk_index.py

Bulk upload documents from JSONL to OpenSearch.
Run from project root: python apps/opensearch/scripts/bulk_index.py SOURCE
  e.g. python apps/opensearch/scripts/bulk_index.py wikipedia
"""
import argparse
import sys
from pathlib import Path

_OPENSEARCH = Path(__file__).resolve().parents[1]
_BACKEND = _OPENSEARCH.parent / "backend"
sys.path.insert(0, str(_OPENSEARCH))
sys.path.insert(0, str(_BACKEND))

import json
import warnings
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk

from paths import DATA_PATH
from config_loader import get_config
from schemas.mappings import mapping

parser = argparse.ArgumentParser(description="Bulk upload JSONL to OpenSearch")
parser.add_argument("source", help="Source name (e.g. wikipedia, mathematica)")
args = parser.parse_args()

SOURCE_NAME = args.source
INDEX_NAME = f"mathmex_{SOURCE_NAME}"
JSONL_FILE_PATH = str(DATA_PATH / f"jsonl/mathmex_{SOURCE_NAME}.jsonl")

config = get_config()
OPENSEARCH_HOST = config.get('opensearch', 'host')
USER = config.get('opensearch_admin', 'username')
PASSWORD = config.get('opensearch_admin', 'password')

# Suppress the security warning from using a self-signed cert
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def get_opensearch_client():
    """Initializes and returns the OpenSearch client."""
    # Create and return the OpenSearch client instance
    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_HOST}],
        http_auth=(USER, PASSWORD),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
        connection_class=RequestsHttpConnection
    )
    return client


def generate_bulk_actions(file_path, index_name):
    """
    Generator function to read a JSONL file and yield documents for bulk indexing.
    This is memory-efficient as it reads the file line by line.
    Args:
        file_path (str): Path to the JSONL file.
        index_name (str): Name of the OpenSearch index.
    Yields:
        dict: Document action for bulk upload.
    """
    with open(file_path, mode='r', encoding='utf-8') as jsonlfile:
        print("Generating documents for bulk upload...")
        for line in jsonlfile:
            document = json.loads(line)
            # Yield each document as a bulk action
            yield {
                "_index": index_name,
                "_source": document,
            }


def ensure_index_exists(client, index_name):
    """Create the index with the explicit mapping if it does not exist."""
    if not client.indices.exists(index=index_name):
        print(f"Index '{index_name}' does not exist. Creating with explicit mapping...")
        client.indices.create(index=index_name, body=mapping)
        print(f"Created index '{index_name}'.")
    else:
        print(f"Index '{index_name}' already exists.")


def main():
    """Main function to run the bulk upload."""
    if not Path(JSONL_FILE_PATH).exists():
        sys.exit(f"JSONL file not found: {JSONL_FILE_PATH}\nRun bin/process.sh {SOURCE_NAME} <tsv_file> first.")

    client = get_opensearch_client()
    ensure_index_exists(client, INDEX_NAME)

    print(f"Starting bulk upload of '{JSONL_FILE_PATH}' to index '{INDEX_NAME}'...")

    try:
        # Perform the bulk upload using the OpenSearch helpers.bulk utility
        success_count, errors = bulk(client, generate_bulk_actions(JSONL_FILE_PATH, INDEX_NAME), chunk_size=100,
                                     request_timeout=60)

        print("\nBulk upload complete!")
        print(f"Successfully indexed: {success_count} documents.")
        print(f"Failed to index: {len(errors)} documents.")

    except Exception as e:
        print(f"\nAn error occurred during the bulk upload: {e}")


if __name__ == "__main__":
    main()
