# upload_tsv.py
import csv
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
import warnings

# --- Configuration ---
# IMPORTANT: Use the 'admin' user for this script as it needs write permissions.
OPENSEARCH_HOST = 'localhost'
OPENSEARCH_PORT = 9200
OPENSEARCH_USER = 'admin'
OPENSEARCH_PASSWORD = 'Str0ngP0ssw0rd' # <-- The admin password you set
INDEX_NAME = 'MathMex'
TSV_FILE_PATH = 'final_wikipedia.tsv'

# The headers of your TSV file in order.
# *** YOU MUST ADJUST THIS TO MATCH YOUR TSV FILE'S COLUMNS ***
TSV_HEADERS = ['Title', 'Description', 'URL']

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
    Generator function to read a TSV file and yield documents for bulk indexing.
    This is memory-efficient as it reads the file line by line.
    """
    with open(file_path, mode='r', encoding='utf-8') as tsvfile:
        # Use csv.reader with tab delimiter for TSV files
        reader = csv.reader(tsvfile, delimiter='\t')
        
        # Skip the header row if your file has one
        # next(reader, None) 
        
        print("Generating documents for bulk upload...")
        for row in reader:
            # Create a dictionary from the headers and the row data
            document = dict(zip(TSV_HEADERS, row))
            
            # Yield the action dictionary for the bulk helper
            yield {
                "_index": index_name,
                "_source": document,
            }

def main():
    """Main function to run the bulk upload."""
    client = get_opensearch_client()
    
    print(f"Starting bulk upload of '{TSV_FILE_PATH}' to index '{INDEX_NAME}'...")
    
    try:
        # The helpers.bulk function is a generator, so we need to iterate over it
        # to execute the upload. It's highly efficient.
        success_count = 0
        fail_count = 0
        
        for ok, action in bulk(client, generate_bulk_actions(TSV_FILE_PATH, INDEX_NAME), chunk_size=500, request_timeout=60):
            if ok:
                success_count += 1
            else:
                fail_count += 1
                print(f"Failed to index document: {action}")

            # Optional: Print progress periodically
            if (success_count + fail_count) % 10000 == 0:
                print(f"Processed {success_count + fail_count} documents...")

        print("\nBulk upload complete!")
        print(f"Successfully indexed: {success_count} documents.")
        print(f"Failed to index: {fail_count} documents.")

    except Exception as e:
        print(f"\nAn error occurred during the bulk upload: {e}")

if __name__ == "__main__":
    main()
