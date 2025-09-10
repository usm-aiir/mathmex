"""
bulk_index.py

Script to bulk upload documents from a JSONL file to an OpenSearch index for MathMex.
Run this script after creating an index and generating a JSONL file with documents.
"""
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
import warnings
import configparser

# --- Load Configuration from config.ini ---
config = configparser.ConfigParser()
config.read('../config.ini')

# OpenSearch Client Configuration from file
OPENSEARCH_HOST = config.get('opensearch', 'host')
OPENSEARCH_PORT = config.getint('opensearch', 'port') # Use getint for numbers
OPENSEARCH_USER = config.get('opensearch', 'admin_user')
OPENSEARCH_PASSWORD = config.get('opensearch', 'admin_password')
INDEX_NAME = config.get('opensearch', 'index_name')
MODEL = config.get('opensearch', 'model')

# Name of the data source and index (change as needed)
SOURCE_NAME = 'math-stack-exchange'
INDEX_NAME = f'mathmex_{SOURCE_NAME}'
JSONL_FILE_PATH = f'../data/jsonl/{SOURCE_NAME}.jsonl'

# Suppress the security warning from using a self-signed cert
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def get_opensearch_client():
    """Initializes and returns the OpenSearch client."""
    # Create and return the OpenSearch client instance
    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
        http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
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


def main():
    """Main function to run the bulk upload."""
    client = get_opensearch_client()

    print(f"Starting bulk upload of '{JSONL_FILE_PATH}' to index '{INDEX_NAME}'...")

    try:
        # Perform the bulk upload using the OpenSearch helpers.bulk utility
        success_count, errors = bulk(client, generate_bulk_actions(JSONL_FILE_PATH, INDEX_NAME), chunk_size=500,
                                     request_timeout=60)

        print("\nBulk upload complete!")
        print(f"Successfully indexed: {success_count} documents.")
        print(f"Failed to index: {len(errors)} documents.")

    except Exception as e:
        print(f"\nAn error occurred during the bulk upload: {e}")


if __name__ == "__main__":
    main()
