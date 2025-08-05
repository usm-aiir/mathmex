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
import re
import os
from llm_answer import generate_llm_answer


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
@app.route("/api/search", methods=["POST"])
def search():
    """
    Search endpoint. Accepts a query and optional filters, performs semantic search using OpenSearch and SentenceTransformer.
    Returns:
        JSON: Search results and total count.
    """
    data = request.get_json()
    query = data.get('query', '')
    sources = data.get('sources', [])
    media_types = data.get('mediaTypes', [])

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Define available sources and their corresponding indices
    source_to_index = {
        'arxiv': 'mathmex_arxiv',
        'math-overflow': 'mathmex_math-overflow',
        'math-stack-exchange': 'mathmex_math-stack-exchange',
        'mathematica': 'mathmex_mathematica',
        'wikipedia': 'mathmex_wikipedia',
        'youtube': 'mathmex_youtube'
    }

    # Filter indices based on selected sources
    if sources:
        indices = [source_to_index[source] for source in sources if source in source_to_index]
    else:
        indices = list(source_to_index.values())


    model = get_model()

    # Convert MathLive query to MathMex data format
    query = format_for_mathmex(query)

    # Vectorize query
    query_vec = model.encode(query).tolist()

    # Build query with filters
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
                                "k": 1000  # Fixed upper limit for KNN
                            }
                        }
                    }
                ]
            }
        }  
    }
    if media_types:
        query_body["query"]["bool"]["filter"] = [
            {"terms": {"media_type": media_types}}
        ]

    response = client.search(
        index=indices,
        body=query_body
    )

    results = []
    for hit in response['hits']['hits']:
        source = hit['_source']
        results.append({
            'title': source.get('title'),
            'media_type': source.get('media_type'),
            'body_text': format_for_mathlive(source.get("body_text")),
            'link': source.get('link'),
            'score': hit.get('_score')
        })

    results = delete_dups(results, unique_key="body_text")
    total = 1000

    # Prepare context for LLM
    context = "\n\n".join([
        f"Title: {r['title']}\nBody: {r['body_text']}" for r in results[:5]
    ])
    prompt = f"Given the following search results, answer the user's query: \"{query}\"\n\nSearch Results:\n{context}\n\nAnswer:"
    print("Prompt sent to LLM:", prompt)
    print("Results for context:", results)
    # Generate answer using Hugging Face model
    try:
        llm_answer = llm(prompt, max_length=256)[0]['generated_text']
    except Exception as e:
        print("LLM generation error:", e)
        llm_answer = ""

    return jsonify({'results': results, 'total': total, 'llm_answer': llm_answer})

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

@app.route("/api/generate-llm-answer", methods=["POST"])
def generate_llm_answer():
    """
    Generate answer using LLM based on search results and query.
    Expects JSON payload with 'results' and 'query'.
    Returns:
        JSON: Generated answer from the LLM.
    """
    data = request.get_json()
    results = data.get("results", [])
    query = data.get("query", "")
    # Use results for context
    context = "\n\n".join([
        f"Title: {r['title']}\nBody: {r['body_text']}" for r in results
    ])
    prompt = f"Given the following search results, answer the user's query: \"{query}\"\n\nSearch Results:\n{context}\n\nAnswer:"
    llm_answer = llm(prompt, max_length=256)[0]['generated_text']
    return jsonify({"llm_answer": llm_answer})

def format_for_mathlive(text: str) -> str:
    """
    Replaces single $...$ wrappers with $$...$$ for MathLive consistency,
    while leaving existing $$...$$ untouched.

    Args:
        text (str): The input string containing LaTeX math.
    Returns:
        str: The string with single $...$ replaced by $$...$$
    """
    # Use a regex to find single $...$ not already part of $$...$$
    # Matches a single $...$ with no extra $ next to it
    pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)')

    return pattern.sub(r'$$\1$$', text)

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

def format_for_mathmex(latex):
    """
    Converts LaTeX like '\\text{abc} x^2 \\text{def} y' to
    'abc $x^2$ def $y$'.

    Args:
        latex (str): The LaTeX string to convert.
    Returns:
        str: The formatted string for storage.
    """
    # Pattern: \text{...}
    text_pattern = re.compile(r'\\text\{([^}]*)\}')
    parts = []
    last_end = 0

    # Find all \text{...} and split
    for m in text_pattern.finditer(latex):
        # Add math before this text, if any
        if m.start() > last_end:
            math_part = latex[last_end:m.start()].strip()
            if math_part:
                parts.append(f"$${math_part}$$")
        # Add the plain text
        parts.append(m.group(1))
        last_end = m.end()
    # Add any trailing math
    if last_end < len(latex):
        math_part = latex[last_end:].strip()
        if math_part:
            parts.append(f"${math_part}$")
    # Join with spaces, remove empty $...$
    return " ".join([p for p in parts if p and p != "$$"])

# Example:
# latex = r"\text{The area is } a^2 \text{ and the perimeter is } 4a"
# print(latex_to_storage_format(latex))
# Output: The area is $a^2$ and the perimeter is $4a$

# Load a model from Hugging Face (e.g., Llama-2, Mistral, or any summarization/QA model)
# Example: using a text-generation pipeline
llm = pipeline("text-generation", model="mistralai/Mistral-7B-v0.1")

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    # Run the Flask development server if this script is executed directly
    app.run(port=FLASK_PORT, debug=FLASK_DEBUG)
