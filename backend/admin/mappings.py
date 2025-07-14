"""
mappings.py

Defines the OpenSearch index mapping for MathMex indices, including KNN vector and text fields.
Import this mapping in admin scripts when creating a new index.
"""
# Mapping definition for MathMex indices
mapping = {
    "settings": {
        "index": {
            "knn": True  # Enable KNN search for semantic queries
        }
    },
    "mappings": {
        "properties": {
            # Title of the document (searchable text)
            "title": {"type": "text"},
            # Type of media (e.g., article, video, pdf)
            "media_type": {"type": "text"},
            # Main content body (searchable text, with fielddata enabled for aggregations)
            "body_text": {"type": "text", "fielddata": True},
            # Vector embedding for semantic search (KNN)
            "body_vector": {
                "type": "knn_vector",
                "dimension": 768,  # Embedding vector size
                "method": {
                    "name": "hnsw",  # HNSW algorithm for KNN
                    "space_type": "cosinesimil",  # Cosine similarity
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 16
                    }
                }
            },
            # Source link (unique identifier for the document)
            "link": {"type": "keyword"}
        }
    }
}
