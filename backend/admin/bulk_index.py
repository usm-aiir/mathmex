import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
import warnings

# --- Configuration ---
# IMPORTANT: Use the 'admin' user for this script as it needs write permissions.
OPENSEARCH_HOST = 'localhost'
OPENSEARCH_PORT = 9200
OPENSEARCH_USER = 'admin'
OPENSEARCH_PASSWORD = 'Str0ngP0ssw0rd'

# Change as needed
INDEX_NAME = 'mathmex_'
JSONL_FILE_PATH = 'combined_data.jsonl'

# Suppress the security warning from using a self-signed cert
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def get_opensearch_client():
    """Initializes and returns the OpenSearch client."""
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
    """
    with open(file_path, mode='r', encoding='utf-8') as jsonlfile:
        print("Generating documents for bulk upload...")
        for line in jsonlfile:
            document = json.loads(line)
            yield {
                "_index": index_name,
                "_source": document,
            }


def main():
    """Main function to run the bulk upload."""
    client = get_opensearch_client()

    print(f"Starting bulk upload of '{JSONL_FILE_PATH}' to index '{INDEX_NAME}'...")

    try:
        success_count, errors = bulk(client, generate_bulk_actions(JSONL_FILE_PATH, INDEX_NAME), chunk_size=500,
                                     request_timeout=60)

        print("\nBulk upload complete!")
        print(f"Successfully indexed: {success_count} documents.")
        print(f"Failed to index: {len(errors)} documents.")

    except Exception as e:
        print(f"\nAn error occurred during the bulk upload: {e}")


if __name__ == "__main__":
    main()
