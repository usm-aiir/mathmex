from flask import Blueprint, request, jsonify
import saytex
from services.models import get_embedding_model
from utils.format import format_for_mathlive
from services.models import get_embedding_model

utility_blueprint = Blueprint("utility", __name__)

@utility_blueprint.route("/summarize", methods=["POST"])
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


@utility_blueprint.route("/speech-to-latex", methods=["POST"])
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
    
    
def llm_response(prompt, response_type="summary"):
    model = get_embedding_model()

    # Replace with real generation logic
    return f"[LLM OUTPUT for {response_type}]\n{prompt}"
