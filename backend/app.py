# Import Flask and CORS libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
import saytex
import re


# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so the frontend (React) can communicate with this backend
CORS(app)

# OpenSearch client
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'Str0ngP0ssw0rd'),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False
)

_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('/home/global/dev/MathMex/backend/models/arq1thru3-finetuned-all-mpnet-jul-27')
    return _model

def clean_for_mathlive(text: str) -> str:
    """
    Replaces single $...$ wrappers with $$...$$ for MathLive consistency,
    while leaving existing $$...$$ untouched.
    """
    # Use a regex to find single $...$ not already part of $$...$$
    # Matches a single $...$ with no extra $ next to it
    pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)')

    return pattern.sub(r'$$\1$$', text)

def delete_dups(list, unique_key="body_text"):
    seen_ids = set()
    unique_dicts = []

    for d in list:
        if d[unique_key] not in seen_ids:
            seen_ids.add(d[unique_key])
            unique_dicts.append(d)

    return unique_dicts

# Route for the root URL
@app.route("/")
def home():
    # Display the most recent cleaned LaTeX and function/operator sent to /search (if any)
    latex = app.config.get("last_latex", None)
    function_latex = app.config.get("last_function_latex", None)

    msg = "Hello, MathMex!<br>"
    msg += f"Last CLEANED LaTeX string from frontend: <code>{latex if latex is not None else 'None'}</code><br>"
    msg += f"Last function/operator from frontend: <code>{function_latex if function_latex is not None else 'None'}</code><br>"
    return msg

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get('latex', '')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    model = get_model()
    query_vec = model.encode(query).tolist()
    response = client.search(
        index=['mathmex_arxiv',
               'mathmex_math-overflow',
               'mathmex_math-stack-exchange',
               'mathmex_mathematica',
               'mathmex_wikipedia',
               'mathmex_youtube'
            ],
        body={
            "size": 10,
            "query": {
                "knn": {
                    "body_vector": {
                        "vector": query_vec,
                        "k": 10
                    }
                }
            }
        }
    )

    results = []
    for hit in response['hits']['hits']:
        source = hit['_source']
        results.append({
            'title': source.get('title'),
            'media_type': source.get('media_type'),
            'body_text': clean_for_mathlive(source.get("body_text")),
            'link': source.get('link'),
            'score': source.get('_score')
        })

    results = delete_dups(results, unique_key="body_text")
    return jsonify({'results': results})

@app.route('/speech-to-latex', methods=['POST'])
def speech_to_latex():
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

def latex_to_storage_format(latex):
    """
    Converts LaTeX like '\\text{abc} x^2 \\text{def} y' to
    'abc $x^2$ def $y$'
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
                parts.append(f"${math_part}$")
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

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
