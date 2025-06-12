# Import Flask and CORS libraries
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so the frontend (React) can communicate with this backend
CORS(app)

# Store the last received LaTex globally
last_latex = ""

# Define a simple route for the root URL
@app.route("/")
def home():
    # Show the last received LaTex, or a default message if none has been received.
     global last_latex 
     if last_latex:
        return f"Hello, MathMex!<br>Last received LaTeX: <code>{last_latex}</code>"
     else:
        return "Hello, MathMex!<br>No LaTeX received yet."

@app.route("/api/search", methods=["POST"])
def search():
    global last_latex
    data = request.get_json()
    latex = data.get("latex", "")
    last_latex = latex
    print(f"Received search request with LaTeX: {latex}")  
    # TODO: Implement your search logic here
    # For now, return a mock response:
    print(f"Returning mock results for LaTex: {latex}")
    return jsonify({
        "results": [
            {
                "title": "Sample Result",
                "formula": latex,
                "description": "This is a mock result.",
                "tags": ["example"],
                "year": "2025"
            }
        ]
    })

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)