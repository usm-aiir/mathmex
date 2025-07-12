from opensearchpy import OpenSearch

# --- CONFIG ---
HOST = 'localhost'
PORT = 9200
USER = 'admin'
PASSWORD = 'Str0ngP0ssw0rd'
INDEX_NAME = 'mathmex_math-stack-exchange'

# --- Connect ---
client = OpenSearch(
    hosts=[{'host': HOST, 'port': PORT}],
    http_auth=(USER, PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

# --- Delete the entire index ---
if client.indices.exists(index=INDEX_NAME):
    client.indices.delete(index=INDEX_NAME)
    print(f"Deleted index '{INDEX_NAME}'.")
else:
    print(f"Index '{INDEX_NAME}' does not exist.")
