from typing import List
from flask import Blueprint, request, jsonify
import os
import threading
import logging

from paths import FORMULA_SEARCH_PATH, setup_formula_search_imports
from utils.format import (
    format_for_mathmex,
    format_for_mathlive,
    format_for_tangent_cft_search,
)
from schemas.indexes import source_to_index
from services.models import get_embedding_model, get_tangent_backend
from services.opensearch import get_opensearch_client

fusion_model = None
formula_search_lock = threading.Lock()

try:
    if FORMULA_SEARCH_PATH.exists():
        setup_formula_search_imports()
        from LateFusionModel.late_fusion_model import LateFusionModel, FusionConfig

        fusion_model = LateFusionModel(FusionConfig(
            method=os.getenv("FUSION_METHOD", "rrf"),
            rrf_k=int(os.getenv("FUSION_RRF_K", "60")),
            weight_formula=float(os.getenv("FUSION_WEIGHT_FORMULA", "0.3")),
            weight_text=float(os.getenv("FUSION_WEIGHT_TEXT", "0.7")),
            hybrid_rrf_weight=float(os.getenv("FUSION_HYBRID_RRF_WEIGHT", "0.5")),
            formula_topk=int(os.getenv("FUSION_FORMULA_TOPK", "100")),
            text_topk=int(os.getenv("FUSION_TEXT_TOPK", "100")),
            final_topk=int(os.getenv("FUSION_FINAL_TOPK", "100")),
        ))
        print("LateFusion model loaded successfully")
    else:
        print("LateFusion: formula-search path not found, fusion disabled")
except Exception as e:
    fusion_model = None
    print(f"LateFusion: failed to load ({type(e).__name__}: {e})")

late_fusion_blueprint = Blueprint("late_fusion", __name__)

@late_fusion_blueprint.route("/fusion-search", methods=["POST"])
def fusion_search():
    """
    Dual-mode search combining structural and semantic retrieval.
    """
    print("Received fusion-search request")
    if fusion_model is None:
        print("Fusion-search: model not loaded, returning 503")
        return jsonify({"error": "Fusion search not available"}), 503
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
        tangent_cft_backend = get_tangent_backend()  # Use the loaded backend from models.py
        if tangent_cft_backend is None:
            print("Fusion-search: TangentCFT backend not loaded, formula path may be text-only")

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

        q_preview = (user_query[:50] + "…") if len(user_query) > 50 else user_query
        print(f"Fusion-search: query=\"{q_preview}\" formulas={formula_count} text={text_count} fusion_used={formula_count > 0}")

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
        print(f"Fusion-search: validation error: {e}")
        logging.warning(f"Fusion search validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Fusion-search: failed ({type(e).__name__}: {e})")
        logging.error("Fusion search failed", exc_info=True)
        # Return more detailed error message for debugging
        import traceback
        error_details = {
            "error": "Internal search error",
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc() if logging.getLogger().isEnabledFor(logging.DEBUG) else None
        }
        return jsonify(error_details), 500


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
