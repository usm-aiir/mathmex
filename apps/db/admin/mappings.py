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
            # Document ID = Order docs occur in TSV; e.g., Doc_0, Doc_1, Doc_2, ...
            "doc_ID": {"type": "text"},
            # Title of the document (searchable text)
            "title": {"type": "text"},
            # Type of media (e.g., article, video, pdf)
            "media_type": {"type": "text"},
            # Main content body (searchable text, with fielddata enabled for aggregations)
            "body": {"type": "text", "fielddata": True},
            # Vector embedding for whole-bodysemantic search (KNN)
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

            # Split text & formula vectors from body_text
            "text_vector": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                }
            },
            
            "formulas": {
                "type": "nested",
                "properties": {
                    "latex": { "type": "text" },
                    "formula_vector": {
                    "type": "knn_vector",
                    "dimension": 300,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib"
                    }
                    }
                }
            },
            # Source link (unique identifier for the document)
            "link": {"type": "keyword"}
        }
    }
}
