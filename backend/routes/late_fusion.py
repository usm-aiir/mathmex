from typing import List
from flask import Blueprint, request, jsonify
import sys
import os
import threading
import logging

from utils.format import (
    format_for_mathmex,
    format_for_mathlive,
    format_for_tangent_cft_search,
)

_ROUTES_DIR = os.path.dirname(os.path.abspath(__file__))

_FORMULA_SEARCH_PATH = os.path.abspath(
    os.path.join(_ROUTES_DIR, "..", "..", "..", "formula-search")
)
_LATE_FUSION_PATH = os.path.join(_FORMULA_SEARCH_PATH, "LateFusionModel")

if _FORMULA_SEARCH_PATH not in sys.path:
    sys.path.insert(0, _FORMULA_SEARCH_PATH)
if _LATE_FUSION_PATH not in sys.path:
    sys.path.insert(0, _LATE_FUSION_PATH)

from LateFusionModel.late_fusion_model import LateFusionModel, FusionConfig

from schemas.indexes import source_to_index

from services.models import get_embedding_model
from services.opensearch import get_opensearch_client
from services.tangent_cft import get_tangent_cft_backend

# Fusion configuration from environment variables
fusion_settings = FusionConfig(
    method=os.getenv("FUSION_METHOD", "rrf"),
    rrf_k=int(os.getenv("FUSION_RRF_K", "60")),
    weight_formula=float(os.getenv("FUSION_WEIGHT_FORMULA", "0.3")),
    weight_text=float(os.getenv("FUSION_WEIGHT_TEXT", "0.7")),
    hybrid_rrf_weight=float(os.getenv("FUSION_HYBRID_RRF_WEIGHT", "0.5")),
    formula_topk=int(os.getenv("FUSION_FORMULA_TOPK", "100")),
    text_topk=int(os.getenv("FUSION_TEXT_TOPK", "100")),
    final_topk=int(os.getenv("FUSION_FINAL_TOPK", "100")),
)

fusion_model = LateFusionModel(fusion_settings)

# Serialize TangentCFT query path mutations
formula_search_lock = threading.Lock()

late_fusion_blueprint = Blueprint("late_fusion", __name__)

@late_fusion_blueprint.route("/fusion-search", methods=["POST"])
def fusion_search():
    """
    Dual-mode search combining structural and semantic retrieval.
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        user_query = request_data.get("query", "")
        selected_sources = request_data.get("sources", [])
        selected_media_types = request_data.get("mediaTypes", [])
        max_results = request_data.get("top_k", 50)

        if not user_query or not user_query.strip():
            return jsonify({"error": "No query provided"}), 400

        # ---- NEW access pattern (process-wide singletons) ----
        text_model = get_embedding_model()
        opensearch_client = get_opensearch_client()
        tangent_cft_backend = get_tangent_cft_backend()

        fused_results = fusion_model.process_query(
            query=user_query,
            tangent_cft_backend=tangent_cft_backend,
            opensearch_client=opensearch_client,
            text_model=text_model,
            source_to_index_map=source_to_index,
            sources=selected_sources,
            media_types=selected_media_types,
            formula_formatter=format_for_tangent_cft_search,
            text_formatter=format_for_mathmex,
            formula_search_lock=formula_search_lock,
        )

        formulas_found = fusion_model._extract_formulas(user_query)

        formula_count = sum(1 for r in fused_results if r.formula_score is not None)
        text_count = sum(1 for r in fused_results if r.text_score is not None)

        final_results = prepare_fusion_response(fused_results)

        return jsonify(
            {
                "results": final_results[:max_results],
                "total": len(final_results),
                "metadata": {
                    "formulas_found": formulas_found,
                    "formula_results_count": formula_count,
                    "text_results_count": text_count,
                    "fusion_used": formula_count > 0,
                },
            }
        )

    except ValueError as e:
        logging.warning(f"Fusion search validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error("Fusion search failed", exc_info=True)
        return jsonify({"error": "Internal search error"}), 500


def prepare_fusion_response(fused_results: List):
    """
    Fetch full document metadata for fused results from OpenSearch.
    """
    opensearch_client = get_opensearch_client()

    output_results = []
    document_cache = {}

    for fused_result in fused_results:
        doc_id = fused_result.doc_id

        if doc_id not in document_cache:
            found = False
            for index_name in source_to_index.values():
                try:
                    document = opensearch_client.get(
                        index=index_name, id=doc_id
                    )
                    document_cache[doc_id] = document["_source"]
                    found = True
                    break
                except Exception:
                    continue

            if not found:
                continue

        doc_metadata = document_cache.get(doc_id)
        if not doc_metadata:
            continue

        output_results.append(
            {
                "title": doc_metadata.get("title"),
                "media_type": doc_metadata.get("media_type"),
                "body_text": format_for_mathlive(
                    doc_metadata.get("body_text", "")
                ),
                "link": doc_metadata.get("link"),
                "score": float(fused_result.fused_score),
                "fusion_info": {
                    "formula_rank": fused_result.formula_rank,
                    "formula_score": float(fused_result.formula_score)
                    if fused_result.formula_score is not None
                    else None,
                    "text_rank": fused_result.text_rank,
                    "text_score": float(fused_result.text_score)
                    if fused_result.text_score is not None
                    else None,
                    "in_both": fused_result.in_both,
                },
            }
        )

    return output_results
