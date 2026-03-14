from flask import Blueprint, request, jsonify
import saytex
from services.models import get_embedding_model, get_generation_model
from utils.format import format_for_mathlive
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
    
    
    # note, if trying to use this function, ensure the generation model is loaded in services/models.py
    # It is defaulted to commented out to save resources
def llm_response(prompt, response_type="summary", fallback="Unable to generate response"):
    # Configure parameters based on response type
    if response_type == "enhancement":
        max_new_tokens = 64
        temperature = 0.3
        min_length = 10
        max_output_length = 300
        cleanup_markers = ["Response:"]

    else:  # summary
        max_new_tokens = 1024
        temperature = 0.7
        min_length = 20
        max_output_length = None
        cleanup_markers = ["COMPREHENSIVE ANSWER:"]
    
    try:
        generation_model = get_generation_model()
        response = generation_model(
            prompt, 
            max_new_tokens=max_new_tokens,
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
