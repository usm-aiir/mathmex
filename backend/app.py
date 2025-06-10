# Import Flask and CORS libraries
from flask import Flask
from flask_cors import CORS

# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) so the frontend (React) can communicate with this backend
CORS(app)

# Define a simple route for the root URL
@app.route("/")
def home():
    # This will return a simple message to confirm the backend is running
    return "Hello, MathMex!"

# Run the Flask development server if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)