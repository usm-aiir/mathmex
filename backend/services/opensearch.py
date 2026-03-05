from opensearchpy import OpenSearch
from flask import current_app
from services.models import get_embedding_model

def init_opensearch(app):
    config = app.config["APP_CONFIG"]

    app.opensearch_client = OpenSearch(
        hosts=[{
            "host": config.get("opensearch", "host"),
            "port": config.getint("opensearch", "port"),
        }],
        http_auth=(
            config.get("dev", "user"),
            config.get("dev", "password"),
        ),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )

def perform_search(query, k=10):
    model = get_embedding_model()
    client = get_opensearch_client()
    
    query_vector = model.encode(query).tolist()

    response = client.search(
        index="formulas",
        body={
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_vector,
                        "k": k
                    }
                }
            }
        }
    )

    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        results.append({
            "title": source.get("title"),
            "body_text": source.get("body_text"),
            "score": hit["_score"],
        })

    return results

def get_opensearch_client():
    return current_app.opensearch_client
