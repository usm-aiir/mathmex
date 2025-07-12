mapping = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "media_type": {"type": "text"},
            "body_text": {"type": "text", "fielddata": True},
            "body_vector": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 16
                    }
                }
            },
            "link": {"type": "keyword"}
        }
    }
}
