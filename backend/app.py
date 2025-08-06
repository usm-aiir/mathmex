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

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        results = perform_search(query, sources, media_types)
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

    try:
        # Generate with appropriate parameters
        response = summarization_model(
            prompt, 
            max_length=1024,
            temperature=0.7,     # Balanced creativity and accuracy
            do_sample=True
        )[0]['generated_text']
        
        # Extract only the answer part (after the prompt)
        summary = response.replace(prompt, '').strip()
        
        # Clean up any artifacts
        if summary.startswith('COMPREHENSIVE ANSWER:'):
            summary = summary.replace('COMPREHENSIVE ANSWER:', '').strip()
        
        # Strip incomplete sentences - end on the last period
        if summary and '.' in summary:
            # Find the last period
            last_period_index = summary.rfind('.')
            if last_period_index != -1:
                # Keep everything up to and including the last period
                summary = summary[:last_period_index + 1].strip()
        
        # Ensure we have a meaningful response
        if not summary or len(summary.strip()) < 20:
            summary = "I need more specific information to provide a comprehensive answer. Please try refining your search query or selecting more relevant sources."

    except Exception as e:
        print("LLM generation error:", e)
        summary = "I'm currently unable to generate a summary. Please check that the backend model is properly loaded and try again."

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
def perform_search(query, sources, media_types):
    if not query:
        raise ValueError("No query provided")

    source_to_index = {
        'arxiv': 'mathmex_arxiv',
        'math-overflow': 'mathmex_math-overflow',
        'math-stack-exchange': 'mathmex_math-stack-exchange',
        'mathematica': 'mathmex_mathematica',
        'wikipedia': 'mathmex_wikipedia',
        'youtube': 'mathmex_youtube'
    }

    indices = [source_to_index[source] for source in sources if source in source_to_index] if sources else list(source_to_index.values())

    model = get_model()
    query_formatted = format_for_mathmex(query)
    query_vec = model.encode(query_formatted).tolist()

    query_body = {
        "from": 0,
        "size": 100,
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
        'score': hit.get('_score')
    } for hit in response['hits']['hits']]

    results = delete_dups(results, unique_key="body_text")
    return results

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
