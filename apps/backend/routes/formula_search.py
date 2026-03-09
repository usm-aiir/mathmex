from flask import Blueprint, request, jsonify, current_app
from opensearchpy.exceptions import (
    ConnectionError as OpenSearchConnectionError,
    AuthorizationException as OpenSearchAuthorizationException,
)
import io
import sys
import os
import tempfile
import csv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.format import format_for_mathmex, format_for_mathlive, format_for_tangent_cft_search
from schemas.indexes import source_to_index
from services.models import get_embedding_model, get_tangent_backend
from routes.utility import llm_response

formula_search_blueprint = Blueprint('formula_search', __name__)

@formula_search_blueprint.route("/search", methods=["POST"])
def formula_search():
    print("Received search request.")
    data = request.get_json()
    sources = data.get('sources', [])
    media_types = data.get('mediaTypes', [])
    do_enhance = data.get('do_enhance', False)
    diversify = data.get('diversify', False)
    raw_query = data.get("query")
    print(f"Received Query: {raw_query}. Running Retrieval")

    query_file = None
    try:
        backend = get_tangent_backend()
        if backend is None:
            results = perform_search(raw_query, sources, media_types, do_enhance, diversify, custom_vec=False)
            return jsonify({'results': results, 'total': len(results)})

        query_ml = format_for_tangent_cft_search(raw_query)
        query_file = write_temp_query_tsv(query_ml)
        backend.data_reader.queries_dir_path = query_file
        ENCODED_FILE_PATH = current_app.config["ENCODED_FILE_PATH"]

        text_trap = io.StringIO()
        old_stdout = sys.stdout

        try:
            sys.stdout = text_trap
            query_vector = backend.retrieval(
                encoded_file_path=ENCODED_FILE_PATH,
                embedding_type=getattr(backend, 'embedding_type', None),
                ignore_full_relative_path=True,
                tokenize_all=False,
                tokenize_number=True,
                streaming=True,
                faiss=True,
                single_query=True,
                do_retrieval=False
            )
            results = perform_search(
                raw_query,
                sources,
                media_types,
                do_enhance,
                diversify,
                custom_vec=True,
                custom_query_vec=query_vector
            )
            # Fallback to text search when formula search returns nothing (e.g. docs have no formulas)
            if not results:
                results = perform_search(raw_query, sources, media_types, do_enhance, diversify, custom_vec=False)
            return jsonify({'results': results, 'total': len(results)})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception:
            results = perform_search(raw_query, sources, media_types, do_enhance, diversify, custom_vec=False)
            return jsonify({'results': results, 'total': len(results)})
        finally:
            sys.stdout = old_stdout
            try:
                if query_file and os.path.exists(query_file):
                    os.remove(query_file)
            except Exception as cleanup_err:
                print(f"Warning: failed to delete temp file {query_file}: {cleanup_err}")
    except OpenSearchConnectionError:
        return jsonify({"error": "Search service unavailable", "detail": "Cannot connect to OpenSearch"}), 503
    except OpenSearchAuthorizationException:
        return jsonify({"error": "Search forbidden", "detail": "OpenSearch user lacks search permissions"}), 403

def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(x) for x in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy(x) for x in obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    else:
        return obj

def perform_search(
    query,
    sources=None,
    media_types=None,
    do_enhance=False,
    diversify=False,
    custom_vec=False,
    custom_query_vec=None
):
    if not query:
        raise ValueError("No query provided")
    if do_enhance:
        prompt = f"""
            You are a mathematics expert. Provide a brief, technical explanation (2-3 sentences) about the mathematical concept or topic: "{query}"
            Focus on key terminology, related concepts, and mathematical relationships that would help in finding relevant academic content.
            Response:
        """
        query = llm_response(prompt, response_type="enhancement", fallback=f"Mathematical concepts related to {query} including definitions, theorems, and applications.")
    indices = (
        [source_to_index[s] for s in sources if s in source_to_index]
        if sources
        else list(source_to_index.values())
    )
    if custom_vec:
        query_vec = custom_query_vec
        # Formula search: KNN on nested formulas.formula_vector (300-dim)
        knn_field = "formulas.formula_vector"
        use_nested = True
    else:
        model = get_embedding_model()
        query_vec = model.encode(format_for_mathmex(query)).tolist()
        # Text search: KNN on body_vector (768-dim); many docs have empty formulas
        knn_field = "body_vector"
        use_nested = False

    if use_nested:
        query_clause = {
            "nested": {
                "path": "formulas",
                "query": {
                    "knn": {knn_field: {"vector": query_vec, "k": 1000}}
                },
                "score_mode": "max"
            }
        }
    else:
        query_clause = {"knn": {knn_field: {"vector": query_vec, "k": 1000}}}

    source_includes = ["title", "media_type", "body_text", "link"]
    if diversify:
        source_includes.append("body_vector")
    query_body = {
        "size": 100,
        "_source": {"includes": source_includes},
        "query": {"bool": {"must": [query_clause]}}
    }
    if media_types:
        query_body["query"]["bool"]["filter"] = [
            {"terms": {"media_type": media_types}}
        ]
    client = current_app.opensearch_client
    response = client.search(index=indices, body=query_body)
    results = [
        {
            "title": hit["_source"].get("title"),
            "media_type": hit["_source"].get("media_type"),
            "body_text": format_for_mathlive(hit["_source"].get("body_text")),
            "link": hit["_source"].get("link"),
            "score": hit["_score"],
        }
        for hit in response["hits"]["hits"]
    ]
    results = delete_dups(results, unique_key="body_text")
    if diversify and len(results) > 1:
        results = mmr(results, query_vec, lambda_param=0.7, k=min(50, len(results)))
    for result in results:
        result.pop('body_vector', None)
    return results

def mmr(results, query_vector, lambda_param=0.7, k=50):
    if len(results) <= 1:
        return results
    doc_vectors = np.array([result['body_vector'] for result in results if result.get('body_vector')])
    query_vec = np.array(query_vector).reshape(1, -1)
    relevance_scores = cosine_similarity(query_vec, doc_vectors)[0]
    selected_indices = []
    remaining_indices = list(range(len(results)))
    best_idx = np.argmax(relevance_scores)
    selected_indices.append(best_idx)
    remaining_indices.remove(best_idx)
    while len(selected_indices) < k and remaining_indices:
        mmr_scores = []
        for idx in remaining_indices:
            relevance = relevance_scores[idx]
            if selected_indices:
                selected_vectors = doc_vectors[selected_indices]
                current_vector = doc_vectors[idx].reshape(1, -1)
                similarities = cosine_similarity(current_vector, selected_vectors)[0]
                max_similarity = np.max(similarities)
            else:
                max_similarity = 0
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
            mmr_scores.append((idx, mmr_score))
        best_idx, _ = max(mmr_scores, key=lambda x: x[1])
        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)
    return [results[idx] for idx in selected_indices]

def write_temp_query_tsv(mathml_string: str):
    """
    Writes a temporary TSV with one query entry matching MSE format.
    Returns the path to the file.
    """
    # Make sure the MathML is not wrapped in extra quotes
    mathml_string = mathml_string.strip().strip('"').strip("'")

    tmp_tsv = tempfile.NamedTemporaryFile(
        mode="w", suffix=".tsv", delete=False, newline='', encoding="utf-8"
    )

    writer = csv.DictWriter(
        tmp_tsv,
        delimiter="\t",
        fieldnames=["id", "topic_id", "thread_id", "type", "formula"]
    )
    writer.writeheader()
    writer.writerow({
        "id": "user_query",
        "topic_id": "A.000",
        "thread_id": "0000000",
        "type": "title",
        "formula": mathml_string
    })
    tmp_tsv.close()
    return tmp_tsv.name

def delete_dups(list, unique_key="body_text"):
    seen_ids = set()
    unique_dicts = []
    for d in list:
        if d[unique_key] not in seen_ids:
            seen_ids.add(d[unique_key])
            unique_dicts.append(d)
    return unique_dicts