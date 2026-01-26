"""
app.py

Main Flask application factory for MathMex backend.
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import configparser
import os

from services.models import load_models
from services.opensearch import init_opensearch

ENCODED_FILE_PATH = "data/jsonl/TangentCFT/encoded.jsonl"
INDEX_PATH = "data/jsonl/TangentCFT/encoded_index.json"
FAISS_INDEX_PATH = "data/jsonl/TangentCFT/slt_index.faiss"

def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    config = configparser.ConfigParser()
    config.read(os.getenv("BACKEND_CONFIG", "config.ini"))
    app.config["APP_CONFIG"] = config
    app.config["ENCODED_FILE_PATH"] = "data/jsonl/TangentCFT/encoded.jsonl"   
    app.config["INDEX_PATH"] = "data/jsonl/TangentCFT/encoded_index.json"
    app.config["FAISS_INDEX_PATH"] = "data/jsonl/TangentCFT/slt_index.faiss"
    
    # Initialize shared services so they can be used by blueprints
    init_opensearch(app)
    load_models()
    from services.tangent_cft import load_tangent_cft
    load_tangent_cft()
    
    # Import and register blueprints
    from routes.formula_search import formula_search_blueprint
    from routes.late_fusion import late_fusion_blueprint
    from routes.utility import utility_blueprint

    # Register blueprints with URL prefix
    app.register_blueprint(formula_search_blueprint, url_prefix="/api")
    app.register_blueprint(late_fusion_blueprint, url_prefix="/api") 
    app.register_blueprint(utility_blueprint, url_prefix="/utility")

    return app


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.getenv("BACKEND_CONFIG", "config.ini"))

    app = create_app()
    app.run(
        port=config.getint("flask_app", "port"),
        debug=config.getboolean("flask_app", "debug"),
        use_reloader=True
    )


