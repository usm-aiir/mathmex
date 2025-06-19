# Import Flask and CORS libraries
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so the frontend (React) can communicate with this backend
CORS(app)

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

@app.route("/api/search", methods=["POST"])
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

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)