from typing import List
from flask import Blueprint, request, jsonify
import sys
import os
import threading

from utils.format import format_for_mathmex, format_for_mathlive, format_for_tangent_cft_search

# Use __file__-based path for reliable imports regardless of working directory
_ROUTES_DIR = os.path.dirname(os.path.abspath(__file__))

# Add formula-search and LateFusionModel to sys.path so utils.tangentcft imports resolve
_FORMULA_SEARCH_PATH = os.path.abspath(os.path.join(_ROUTES_DIR, '..', '..', '..', 'formula-search'))
_LATE_FUSION_PATH = os.path.join(_FORMULA_SEARCH_PATH, 'LateFusionModel')

if _FORMULA_SEARCH_PATH not in sys.path:
    sys.path.insert(0, _FORMULA_SEARCH_PATH)
if _LATE_FUSION_PATH not in sys.path:
    sys.path.insert(0, _LATE_FUSION_PATH)

from LateFusionModel.late_fusion_model import LateFusionModel, FusionConfig

# Load fusion configuration from environment variables with sensible defaults
fusion_settings = FusionConfig(
    method=os.getenv("FUSION_METHOD", "rrf"),
    rrf_k=int(os.getenv("FUSION_RRF_K", "60")),
    weight_formula=float(os.getenv("FUSION_WEIGHT_FORMULA", "1.0")),
    weight_text=float(os.getenv("FUSION_WEIGHT_TEXT", "1.0")),
    hybrid_rrf_weight=float(os.getenv("FUSION_HYBRID_RRF_WEIGHT", "0.5")),
    formula_topk=int(os.getenv("FUSION_FORMULA_TOPK", "100")),
    text_topk=int(os.getenv("FUSION_TEXT_TOPK", "100")),
    final_topk=int(os.getenv("FUSION_FINAL_TOPK", "100")),
)
fusion_model = LateFusionModel(fusion_settings)

# Small lock to serialize updates to the TangentCFT query path
# guards concurrent requests from overwriting `queries_dir_path`
formula_search_lock = threading.Lock()

# mapping of user-facing source keys to OpenSearch index names.
SOURCE_TO_INDEX = {
    "arxiv": "mathmex_arxiv",
    "math-overflow": "mathmex_math-overflow",
    "math-stack-exchange": "mathmex_math-stack-exchange",
    "mathematica": "mathmex_mathematica",
    "wikipedia": "mathmex_wikipedia",
    "youtube": "mathmex_youtube",
    "proof-wiki": "mathmex_proof-wiki",
    "wikimedia": "mathmex_wikimedia",
}

late_fusion_blueprint = Blueprint('late_fusion', __name__)


@late_fusion_blueprint.route('/api/fusion-search', methods=['POST'])
def fusion_search():
    """
    Dual-mode search combining structural and semantic retrieval.
    """
    from app import backend as formula_backend, client as opensearch_client, get_model
    import logging
    
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
            
        user_query = request_data.get('query', '')
        selected_sources = request_data.get('sources', [])
        selected_media_types = request_data.get('mediaTypes', [])
        max_results = request_data.get('top_k', 50)
        
        if not user_query or not user_query.strip():
            return jsonify({'error': 'No query provided'}), 400
    
        text_model = get_model()
        
        # Model handles formula extraction, retrieval, and fusion
        fused_results = fusion_model.process_query(
            query=user_query,
            tangent_cft_backend=formula_backend,
            opensearch_client=opensearch_client,
            text_model=text_model,
            source_to_index_map=SOURCE_TO_INDEX,
            sources=selected_sources,
            media_types=selected_media_types,
            formula_formatter=format_for_tangent_cft_search,
            text_formatter=format_for_mathmex,
            formula_search_lock=formula_search_lock
        )
        
        formulas_found = fusion_model._extract_formulas(user_query)
        
        # Count how many results came from formula vs text
        formula_count = sum(1 for r in fused_results if r.formula_score is not None)
        text_count = sum(1 for r in fused_results if r.text_score is not None)
        
        # Prepare response with full document metadata
        final_results = prepare_fusion_response(fused_results)
        
        return jsonify({
            'results': final_results[:max_results],
            'total': len(final_results),
            'metadata': {
                'formulas_found': formulas_found,
                'formula_results_count': formula_count,
                'text_results_count': text_count,
                'fusion_used': formula_count > 0
            }
        })
    except ValueError as e:
        logging.warning(f"Fusion search validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Fusion search failed: {e}", exc_info=True)
        return jsonify({'error': 'Internal search error'}), 500

def prepare_fusion_response(fused_results: List):
    """
    Fetch full document metadata for fused results from OpenSearch.
    """
    from app import client as opensearch_client
    from utils.format import format_for_mathlive    
    
    output_results = []
    document_cache = {}
    
    for fused_result in fused_results:
        doc_id = fused_result.doc_id
        
        # Fetch document from OpenSearch if not already cached
        if doc_id not in document_cache:
            # Try all indices to find the document
            indices_to_try = list(SOURCE_TO_INDEX.values())
            
            found = False
            for index_name in indices_to_try:
                try:
                    document = opensearch_client.get(index=index_name, id=doc_id)
                    document_cache[doc_id] = document['_source']
                    found = True
                    break
                except Exception:
                    continue

            if not found:
                print(f"Document {doc_id} not found in any index, skipping from results")
                continue
        
        doc_metadata = document_cache.get(doc_id)
        if not doc_metadata:
            continue
        
        # Build response with fusion metadata
        # Use 'is not None' checks to correctly handle score values of 0.0
        output_results.append({
            'title': doc_metadata.get('title'),
            'media_type': doc_metadata.get('media_type'),
            'body_text': format_for_mathlive(doc_metadata.get('body_text', '')),
            'link': doc_metadata.get('link'),
            'score': float(fused_result.fused_score),
            'fusion_info': {
                'formula_rank': fused_result.formula_rank,
                'formula_score': float(fused_result.formula_score) if fused_result.formula_score is not None else None,
                'text_rank': fused_result.text_rank,
                'text_score': float(fused_result.text_score) if fused_result.text_score is not None else None,
                'in_both': fused_result.in_both
            }
        })
    
    return output_results