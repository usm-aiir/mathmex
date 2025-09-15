"""
app.py

Main Flask application for the MathMex backend API.
Handles search, speech-to-LaTeX, and utility endpoints for the frontend.
Integrates with OpenSearch and SentenceTransformer for semantic search.
"""
# Import Flask and CORS libraries
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import configparser
import saytex
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.format import format_for_mathmex, format_for_mathlive

# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so the frontend (React) can communicate with this backend
CORS(app)

# Load environment variables
load_dotenv()

# --- Load Configuration from config.ini ---
config = configparser.ConfigParser()
config.read( os.getenv("BACKEND_CONFIG") )

# OpenSearch Client Configuration from file
OPENSEARCH_HOST = config.get('opensearch', 'host')
OPENSEARCH_PORT = config.getint('opensearch', 'port') # Use getint for numbers
OPENSEARCH_USER = config.get('opensearch', 'admin_user')
OPENSEARCH_PASSWORD = config.get('opensearch', 'admin_password')
INDEX_NAME = config.get('opensearch', 'index_name')
MODEL = config.get('opensearch', 'model')

# Flask App Configuration from file
FLASK_PORT = config.getint('flask_app', 'port')
FLASK_DEBUG = config.getboolean('flask_app', 'debug')

# OpenSearch client
client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

_model = None
def get_model():
    """
    Loads and caches the SentenceTransformer model for semantic search.
    Returns:
        SentenceTransformer: The loaded model instance.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL)
    return _model

# Model for results summary
summarization_model = pipeline("text-generation", model="mistralai/Mistral-7B-v0.1")

@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get('query', '')
    sources = data.get('sources', [])
    media_types = data.get('mediaTypes', [])
    do_enhance = data.get('do_enhance', False)
    diversify = data.get('diversify', False) 
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        results = perform_search(query, sources, media_types, do_enhance, diversify)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'results': results, 'total': len(results)})

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    query = data.get('query', '')
    sources = data.get('results', [])

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Prepare context for LLM with better structure
    context_sources = []
    for i, r in enumerate(sources, 1):
        source_text = f"[Source {i}] {r['title']}\n{r['body_text']}\n"
        context_sources.append(source_text)
    
    context = "\n".join(context_sources)

    prompt = f"""
        You are an expert mathematics AI assistant. 
        Your task is to provide a comprehensive, accurate, and well-structured answer relevant to the provided search results.

        USER QUERY: "{query}"
        
        SEARCH RESULTS:
        {context}
        
        COMPREHENSIVE ANSWER:
    """

    summary = llm_response(
        prompt=prompt,
        response_type="summary",
        fallback=f"I need more specific information to provide a comprehensive answer. Please try refining your search query or selecting more relevant sources."
    )

    return jsonify({'summary': format_for_mathlive(summary)})


@app.route('/api/speech-to-latex', methods=['POST'])
def speech_to_latex():
    """
    Converts spoken math (text) to LaTeX using SayTeX.
    Returns:
        JSON: The generated LaTeX string or error message.
    """
    data = request.get_json()
    print(f"Received data: {data}")
    text = data.get('text')
    if not text:
        print("Error: No text provided")
        return jsonify({'error': 'No text provided'}), 400

    # Pre-process text to be more SayTeX-friendly
    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "divided by": "/",
        "over": "/",
        "equals": "=",
        "squared": "^2",
        "cubed": "^3",
    }

    for word, symbol in replacements.items():
        text = text.replace(symbol, word)

    print(f"Pre-processed text: {text}")

    try:
        st = saytex.Saytex()
        latex_string = st.to_latex(text)
        print(f"Generated LaTeX: {latex_string}")
        return jsonify({'latex': latex_string})

    except Exception as e:
        print(f"Error during LaTeX conversion: {e}")
        return jsonify({'error': str(e)}), 500

# # # UTIL FUNCTIONS # # #
def perform_search(query, sources, media_types, do_enhance=False, diversify=False):
    if not query:
        raise ValueError("No query provided")

    # If enhanced search is enabled, augment the query with AI response
    if do_enhance:
        prompt = f"""
            You are a mathematics expert. Provide a brief, technical explanation (2-3 sentences) about the mathematical concept or topic: "{query}"
        
            Focus on key terminology, related concepts, and mathematical relationships that would help in finding relevant academic content.
            
            Response:
        """

        ai_response = llm_response(prompt, response_type="enhancement", fallback=f"Mathematical concepts related to {query} including definitions, theorems, and applications.")
        query = f"{query} {ai_response}"

    source_to_index = {
        'arxiv': 'mathmex_arxiv',
        'math-overflow': 'mathmex_math-overflow',
        'math-stack-exchange': 'mathmex_math-stack-exchange',
        'mathematica': 'mathmex_mathematica',
        'wikipedia': 'mathmex_wikipedia',
        'youtube': 'mathmex_youtube',
        'proof-wiki': 'mathmex_proof-wiki'
    }

    indices = [source_to_index[source] for source in sources if source in source_to_index] if sources else list(source_to_index.values())

    model = get_model()
    query_formatted = format_for_mathmex(query)
    query_vec = model.encode(query_formatted).tolist()

    query_body = {
        "from": 0,
        "size": 100,
        "_source": {"includes": ["title", "media_type", "body_text", "link", "body_vector"]},  # Include vectors
        "query": {
            "bool": {
                "must": [
                    {
                        "knn": {
                            "body_vector": {
                                "vector": query_vec,
                                "k": 1000
                            }
                        }
                    }
                ]
            }
        }
    }

    if media_types:
        query_body["query"]["bool"]["filter"] = [{"terms": {"media_type": media_types}}]

    response = client.search(index=indices, body=query_body)

    results = [{
        'title': hit['_source'].get('title'),
        'media_type': hit['_source'].get('media_type'),
        'body_text': format_for_mathlive(hit['_source'].get("body_text")),
        'link': hit['_source'].get('link'),
        'score': hit.get('_score'),
        'body_vector': hit['_source'].get('body_vector')  # Include vector for MMR
    } for hit in response['hits']['hits']]

    results = delete_dups(results, unique_key="body_text")
    
    # Apply MMR for result diversification (only if enabled)
    if diversify and len(results) > 1:
        results = mmr(results, query_vec, lambda_param=0.7, k=min(50, len(results)))
    
    # Clean up results (remove vectors from output)
    for result in results:
        result.pop('body_vector', None)
    
    return results

def mmr(results, query_vector, lambda_param=0.7, k=50):
    if len(results) <= 1:
        return results
    
    # Extract pre-computed document vectors from results
    doc_vectors = np.array([result['body_vector'] for result in results if result.get('body_vector')])
    
    # Convert query vector to numpy array for calculations
    query_vec = np.array(query_vector).reshape(1, -1)
    
    # Calculate relevance scores (similarity to query)
    relevance_scores = cosine_similarity(query_vec, doc_vectors)[0]
    
    # MMR algorithm
    selected_indices = []
    remaining_indices = list(range(len(results)))
    
    # Select first document (highest relevance)
    best_idx = np.argmax(relevance_scores)
    selected_indices.append(best_idx)
    remaining_indices.remove(best_idx)
    
    # Select remaining documents using MMR
    while len(selected_indices) < k and remaining_indices:
        mmr_scores = []
        
        for idx in remaining_indices:
            # Relevance component
            relevance = relevance_scores[idx]
            
            # Diversity component (maximum similarity to already selected docs)
            if selected_indices:
                selected_vectors = doc_vectors[selected_indices]
                current_vector = doc_vectors[idx].reshape(1, -1)
                similarities = cosine_similarity(current_vector, selected_vectors)[0]
                max_similarity = np.max(similarities)
            else:
                max_similarity = 0
            
            # MMR score: λ * relevance - (1-λ) * max_similarity
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
            mmr_scores.append((idx, mmr_score))
        
        # Select document with highest MMR score
        best_idx, _ = max(mmr_scores, key=lambda x: x[1])
        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)
    
    # Return reordered results
    return [results[idx] for idx in selected_indices]

def llm_response(prompt, response_type="summary", fallback="Unable to generate response"):
    # Configure parameters based on response type
    if response_type == "enhancement":
        max_length = 64
        temperature = 0.3
        min_length = 10
        max_output_length = 300
        cleanup_markers = ["Response:"]

    else:  # summary
        max_length = 1024
        temperature = 0.7
        min_length = 20
        max_output_length = None
        cleanup_markers = ["COMPREHENSIVE ANSWER:"]
    
    try:
        response = summarization_model(
            prompt, 
            max_length=max_length,
            temperature=temperature,
            do_sample=True
        )[0]['generated_text']
        
        # Extract only the answer part (after the prompt)
        generated_text = response.replace(prompt, '').strip()
        
        # Clean up any artifacts
        for marker in cleanup_markers:
            if generated_text.startswith(marker):
                generated_text = generated_text.replace(marker, '').strip()
        
        # Summary-specific cleanup: strip incomplete sentences at the last period
        if response_type == "summary" and generated_text and '.' in generated_text:
            last_period_index = generated_text.rfind('.')
            if last_period_index != -1:
                generated_text = generated_text[:last_period_index + 1].strip()
        
        # Ensure we have a meaningful response
        if not generated_text or len(generated_text.strip()) < min_length:
            return fallback
        
        # Truncate if too long (for enhancement only)
        if max_output_length and len(generated_text) > max_output_length:
            generated_text = generated_text[:max_output_length] + "..."
            
        return generated_text

    except Exception as e:
        print(f"LLM generation error ({response_type}): {e}")
        return fallback

def delete_dups(list, unique_key="body_text"):
    """
    Removes duplicate dictionaries from a list based on a unique key.

    Args:
        list (list): List of dictionaries.
        unique_key (str): Key to determine uniqueness.
    Returns:
        list: List with duplicates removed.
    """
    seen_ids = set()
    unique_dicts = []

    for d in list:
        if d[unique_key] not in seen_ids:
            seen_ids.add(d[unique_key])
            unique_dicts.append(d)

    return unique_dicts

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    # Run the Flask development server if this script is executed directly
    app.run(port=FLASK_PORT, debug=FLASK_DEBUG)
