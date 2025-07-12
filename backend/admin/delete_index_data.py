from opensearchpy import OpenSearch, ConnectionTimeout

# --- CONFIG ---
HOST = 'localhost'
PORT = 9200
USER = 'admin'
PASSWORD = 'Str0ngP0ssw0rd'
INDEX_NAME = 'mathmex*'

# --- Connect ---
client = OpenSearch(
    hosts=[{'host': HOST, 'port': PORT}],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)


try:
    # --- Delete all documents ---
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
