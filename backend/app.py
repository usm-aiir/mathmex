# Import Flask and CORS libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
import saytex

# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so the frontend (React) can communicate with this backend
CORS(app, origins=["https://mathmex.com", "https://www.mathmex.com"])

# Route for the root URL
@app.route("/")
def home():
    # Display the most recent cleaned LaTeX and function/operator sent to /api/search (if any)
    latex = app.config.get("last_latex", None)
    function_latex = app.config.get("last_function_latex", None)

    # Clean the LaTeX for display (replace "\ " with real spaces)
    latex_cleaned = latex.replace("\\ ", " ") if latex else None
    function_latex_cleaned = function_latex.replace("\\ ", " ") if function_latex else None

    msg = "Hello, MathMex!<br>"
    msg += f"Last CLEANED LaTeX string from frontend: <code>{latex_cleaned if latex_cleaned is not None else 'None'}</code><br>"
    msg += f"Last function/operator from frontend: <code>{function_latex_cleaned if function_latex_cleaned is not None else 'None'}</code><br>"
    return msg

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    latex = data.get("latex", "")  # full LaTeX string from the search bar
    function_latex = data.get("functionLatex", "")  # LaTeX for function/operator

    # Store the latest values in app config so they can be shown on the home page
    app.config["last_latex"] = latex
    app.config["last_function_latex"] = function_latex

    # Print the raw string received from the frontend
    print(f"Raw LaTeX from frontend: {latex!r}")
    print(f"Raw functionLatex from frontend: {function_latex!r}")

    # Clean only for logging
    latex_cleaned = latex.replace("\\ ", " ")
    function_latex_cleaned = function_latex.replace("\\ ", " ")

    print(f"Received search request with LaTeX: {latex_cleaned}")
    print(f"Received function/operator LaTeX: {function_latex_cleaned}")

    # Always return the functionLatex field, even if it's empty
    return jsonify({
        "results": [
            {
                "title": "Sample Result",
                "formula": latex if latex else None,
                "functionLatex": function_latex,  # Always include, even if empty string
                "description": "This is a mock result.",
                "tags": ["example"],
                "year": "2025"
            }
        ]
    })

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

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
