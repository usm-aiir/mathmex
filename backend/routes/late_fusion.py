from typing import List
from flask import Blueprint, request, jsonify
import sys
import os
import re
import csv
import tempfile
import threading

from utils.format import format_for_mathmex, format_for_mathlive, format_for_tangent_cft_search

sys.path.append(os.path.abspath('../../formula-search'))  
from LateFusionModel.late_fusion_model import LateFusionModel, RetrievalResult, FusionConfig
from Embedding_Preprocessing.encoder_tuple_level import TupleTokenizationMode

# uses default settings defined in late fusion. Change the params if needed.
fusion_settings = FusionConfig()
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
    
    Formulas capture mathematical structure that text embeddings miss,
    while text captures context and intent. Fusion exploits both signals.
    Fallback to text-only prevents poor formula matches from degrading results.
    """
    request_data = request.get_json()
    user_query = request_data.get('query', '')
    selected_sources = request_data.get('sources', [])
    selected_media_types = request_data.get('mediaTypes', [])
    max_results = request_data.get('top_k', 50)
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    formulas_found = extract_math_formulas(user_query)
    
    formula_search_results = []
    
    if formulas_found:
        # First formula typically represents primary mathematical intent
        main_formula = formulas_found[0]
        formula_search_results = search_using_formula(
            main_formula, 
            selected_sources, 
            selected_media_types,
            max_results=100
        )
    
    # Text embeddings capture semantic relationships that formula structure alone misses
    text_search_results = search_using_text(
        user_query, 
        selected_sources, 
        selected_media_types,
        max_results=200
    )
    
    # Fusion degrades quality when formula results are too sparse or low-confidence
    if formula_search_results and len(formula_search_results) >= fusion_settings.min_formula_results:
        combined_results = fusion_model.fuse(formula_search_results, text_search_results)
        final_results = prepare_fusion_response(combined_results)
        did_use_fusion = True
    else:
        final_results = prepare_text_only_response(text_search_results[:max_results])
        did_use_fusion = False
    
    return jsonify({
        'results': final_results[:max_results],
        'total': len(final_results),
        'metadata': {
            'formulas_found': formulas_found,
            'formula_results_count': len(formula_search_results),
            'text_results_count': len(text_search_results),
            'fusion_used': did_use_fusion
        }
    })


def extract_math_formulas(text: str) -> List[str]:
    """
    Extract LaTeX formulas from text.
    
    Multiple delimiters and fallback patterns handle diverse input formats
    since users may paste from various sources (papers, StackExchange, etc.).
    Deduplication prevents redundant searches on repeated formulas.
    """
    # Base case
    if not text:
        return []
    
    extracted_formulas = []
    
    # Escaped dollars in LaTeX source should remain literal, not trigger extraction
    escaped_dollar_placeholder = "__ESCAPED_DOLLAR__"
    text_working_copy = text.replace(r"\$", escaped_dollar_placeholder)
    
    # Extract display math ($$...$$)
    display_formulas = re.findall(r'\$\$(.+?)\$\$', text_working_copy, flags=re.DOTALL)
    extracted_formulas.extend(display_formulas)
    
    # Extract inline math ($...$)
    # Remove display math first to avoid matching $ inside $$...$$
    text_without_display_math = re.sub(r'\$\$(.+?)\$\$', '', text_working_copy, flags=re.DOTALL)
    inline_formulas = re.findall(r'\$([^$]+?)\$', text_without_display_math)
    extracted_formulas.extend(inline_formulas)
    
    # Fallback: if no delimited formulas found, check if the whole string looks mathematical
    if not extracted_formulas:
        # Remove any \text{...} commands since they're natural language
        potential_formula = re.sub(r'\\text\{[^}]*\}', '', text).strip()
        # Remove leading non-math characters like "Formula:"
        potential_formula = re.sub(r'^\s*[^a-zA-Z0-9\\]*:', '', potential_formula).strip()
        
        # Patterns that indicate mathematical content
        math_indicators = [
            r'[a-zA-Z]\^[\d{]',      # Exponents like x^2
            r'[a-zA-Z]_[\d{]',       # Subscripts like a_n
            r'\\frac\{',             # Fractions
            r'\\sqrt[\[{]',          # Square roots
            r'\\sum\b',              # Summations
            r'\\int\b',              # Integrals
            r'[+\-*/=<>≤≥≠]',        # Mathematical operators
        ]
        
        contains_math = any(re.search(pattern, potential_formula) for pattern in math_indicators)
        
        if contains_math and len(potential_formula) > 1:
            # Clean up leading/trailing non-word characters except LaTeX backslashes
            potential_formula = re.sub(r'^[^\w\\]+|[^\w}]+$', '', potential_formula)
            if potential_formula and not potential_formula.isspace():
                extracted_formulas.append(potential_formula)
    
    # Clean up formulas and filter out invalid ones
    cleaned_formulas = []
    for formula in extracted_formulas:
        # Restore escaped dollar signs
        formula = formula.strip().replace(escaped_dollar_placeholder, r"\$")
        
        # Filter out plain numbers, whitespace, and plain text
        if (len(formula) > 1 and 
            not formula.isdigit() and 
            not formula.isspace() and
            not formula.isalpha()):
            cleaned_formulas.append(formula)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(cleaned_formulas))

def search_using_formula(formula: str, sources: List[str], media_types: List[str], max_results: int = 100) -> List[RetrievalResult]:
    """
    Search for structurally similar formulas using TangentCFT embeddings in OpenSearch.
    
    OpenSearch nested KNN allows direct vector similarity search without file I/O,
    making retrieval faster and avoiding race conditions from temporary files.
    """
    from app import backend as formula_backend, client as opensearch_client
    
    # TangentCFT requires encoded tuples, not raw LaTeX
    formula_in_mathml = format_for_tangent_cft_search(formula)
    
    # Create temporary query TSV since TangentCFT backend expects this format
    query_file = create_temporary_query_file(formula_in_mathml)
    
    # Lock to prevent concurrent requests from overwriting each other's query path
    with formula_search_lock:
        formula_backend.data_reader.queries_dir_path = query_file
        
        try:
            # Generate query vector without retrieval (do_retrieval=False returns just the vector)
            query_vector = formula_backend.retrieval(
            encoded_file_path="data/jsonl/TangentCFT/encoded.jsonl",
            embedding_type=TupleTokenizationMode(3),
            ignore_full_relative_path=True,
            tokenize_all=False,
            tokenize_number=True,
            streaming=True,
            faiss=True,
            single_query=True,
            do_retrieval=False  # Only compute query vector, skip retrieval
            )
            
            # OpenSearch uses nested fields for formulas; use the global mapping
            indices_to_search = [SOURCE_TO_INDEX[s] for s in sources if s in SOURCE_TO_INDEX] if sources else list(SOURCE_TO_INDEX.values())
        
            # Nested KNN query structure for formula vectors
            query_body = {
                "size": max_results,
                "_source": {
                    "includes": ["title", "media_type", "body_text", "link"]
                },
                "query": {
                    "bool": {
                        "must": [
                            {
                                "nested": {
                                    "path": "formulas",
                                    "query": {
                                        "knn": {
                                            "formulas.formula_vector": {
                                                "vector": query_vector.tolist() if hasattr(query_vector, 'tolist') else query_vector,
                                                "k": max_results
                                            }
                                        }
                                    },
                                    "score_mode": "max"  # Use highest-scoring formula per document
                                }
                            }
                        ]
                    }
                }
            }
            
            # Media type filtering improves precision when user specifies content type
            if media_types:
                query_body["query"]["bool"]["filter"] = [
                    {"terms": {"media_type": media_types}}
                ]
            
            # Execute OpenSearch query
            response = opensearch_client.search(index=indices_to_search, body=query_body)
            
            # Convert to RetrievalResult format for fusion
            results_with_metadata = []
            for rank, hit in enumerate(response["hits"]["hits"], start=1):
                results_with_metadata.append(RetrievalResult(
                    doc_id=hit["_id"],
                    score=float(hit["_score"]),
                    rank=rank,
                    source='formula',
                    metadata={
                        '_id': hit['_id'],
                        'title': hit['_source'].get('title', ''),
                        'media_type': hit['_source'].get('media_type', ''),
                        'body_text': hit['_source'].get('body_text', ''),
                        'link': hit['_source'].get('link', ''),
                        'score': float(hit['_score'])
                    }
                ))
            
            return results_with_metadata
            
        finally:
            # Cleanup prevents disk bloat from concurrent requests
            if query_file and os.path.exists(query_file):
                os.unlink(query_file)


def search_using_text(query: str, sources: List[str], media_types: List[str], max_results: int = 200) -> List[RetrievalResult]:
    """
    Semantic text search using sentence embeddings and k-NN in OpenSearch.
    
    Vector similarity captures conceptual relevance beyond keyword matching,
    crucial for mathematical queries where terminology varies across domains.
    """
    # use the already-loaded models
    from app import get_model, client as opensearch_client
    text_model = get_model()
    
    # Format query and convert to embedding vector
    formatted_query = format_for_mathmex(query)
    query_vector = text_model.encode(formatted_query).tolist()
    
    # Use global mapping to determine which indices to query
    indices_to_search = [SOURCE_TO_INDEX[s] for s in sources if s in SOURCE_TO_INDEX] if sources else list(SOURCE_TO_INDEX.values())
    
    # Build k-NN search query
    search_query = {
        "from": 0,
        "size": max_results,
        "_source": {"includes": ["title", "media_type", "body_text", "link"]},
        "query": {
            "bool": {
                "must": [
                    {
                        "knn": {
                            "body_vector": {
                                "vector": query_vector,
                                "k": max_results
                            }
                        }
                    }
                ]
            }
        }
    }
    
    # Add media type filter if specified
    if media_types:
        search_query["query"]["bool"]["filter"] = [{"terms": {"media_type": media_types}}]
    
    search_response = opensearch_client.search(index=indices_to_search, body=search_query)
    
    # Convert OpenSearch results to our RetrievalResult format
    text_results = []
    for position, hit in enumerate(search_response['hits']['hits'], start=1):
        text_results.append(RetrievalResult(
            doc_id=hit.get('_id', hit['_source'].get('link', f"doc_{position}")),
            score=hit.get('_score', 0.0),
            rank=position,
            source='text',
            metadata={
                '_id': hit['_id'],
                'title': hit['_source'].get('title'),
                'media_type': hit['_source'].get('media_type'),
                'body_text': hit['_source'].get('body_text'),
                'link': hit['_source'].get('link'),
                'score': hit.get('_score', 0.0)
            }
        ))
    
    return text_results


def prepare_fusion_response(fused_results: List):
    """
    Fetch full document metadata for fused results.
    
    Fusion output contains only doc IDs and scores; OpenSearch provides
    actual content needed for display. Caching prevents redundant lookups
    since documents may appear in both retrieval streams.
    Fusion metadata helps users understand ranking decisions.
    """
    output_results = []
    from app import client as opensearch_client
    
    document_cache = {}
    
    # Example of FusedResults structure:
    # fused_results = [
    #     FusedResult(
    #         doc_id='123123',
    #         fused_score=2.5,
    #         formula_rank=1,
    #         formula_score=1.8,
    #         text_rank=3,
    #         text_score=0.7,
    #         in_both=True
    #     ),
    # ]
    for fused_result in fused_results:
        doc_id = fused_result.doc_id
        
        # Fetch document from OpenSearch if not already cached
        """
        Example document structure in OpenSearch:
        "doc_id": {
            "title": "On the Convergence of Series",
            "media_type": "arxiv",
            "body_text": "We show that the series \\sum_{n=1}^\\infty ...",
            "link": "https://arxiv.org/abs/1234.5678",
            "body_vector": [0.012, -0.334, 0.221, ...],
            "other_meta": {"authors": ["A. Author"], "year": 2020}
        },
        """
        if doc_id not in document_cache:

            # Use global mapping to try all indices when fetching document metadata
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
                continue
        
        doc_metadata = document_cache.get(doc_id)
        if not doc_metadata:
            continue
        
        # Build response with fusion metadata
        output_results.append({
            'title': doc_metadata.get('title'),
            'media_type': doc_metadata.get('media_type'),
            'body_text': format_for_mathlive(doc_metadata.get('body_text', '')),
            'link': doc_metadata.get('link'),
            'score': float(fused_result.fused_score),
            'fusion_info': {
                'formula_rank': fused_result.formula_rank,
                'formula_score': float(fused_result.formula_score) if fused_result.formula_score else None,
                'text_rank': fused_result.text_rank,
                'text_score': float(fused_result.text_score) if fused_result.text_score else None,
                'in_both': fused_result.in_both
            }
        })
    
    return output_results


def prepare_text_only_response(text_results: List[RetrievalResult]):
    """
    Format text-only results without fusion overhead.
    
    Skipping fusion logic when formulas are absent/insufficient
    reduces latency and avoids unnecessary complexity.
    """
    output_results = []
    
    for result in text_results:
        doc_info = result.metadata
        output_results.append({
            'title': doc_info.get('title'),
            'media_type': doc_info.get('media_type'),
            'body_text': format_for_mathlive(doc_info.get('body_text', '')),
            'link': doc_info.get('link'),
            'score': float(result.score)
        })
    
    return output_results


def create_temporary_query_file(mathml_string: str):
    """
    Create a temporary TSV file for TangentCFT query.
    
    TSV format matches TangentCFT's training data structure (ARQMath),
    ensuring consistent encoding behavior. Temporary files isolate
    concurrent requests from interfering with each other.
    """
    mathml_string = mathml_string.strip().strip('"').strip("'")
    
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", 
        suffix=".tsv", 
        delete=False, 
        newline='', 
        encoding="utf-8"
    )
    
    tsv_writer = csv.DictWriter(
        temp_file,
        delimiter="\t",
        fieldnames=["id", "topic_id", "thread_id", "type", "formula"]
    )
    tsv_writer.writeheader()
    tsv_writer.writerow({
        "id": "user_query",
        "topic_id": "A.000",
        "thread_id": "0000000",
        "type": "title",
        "formula": mathml_string
    })
    temp_file.close()
    
    return temp_file.name