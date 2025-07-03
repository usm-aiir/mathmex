"""
USAGE:
Spinning up OpenSearch:
From server_host terminal run: python3 app.py 


Connecting to OpenSearch Dashboard: 
In terminal run: ssh -L [LOCAL_PORT]:[DESTINATION_HOSTNAME]:[DESTINATION_PORT] [USER]@[SERVER_HOST]
Example: ssh -L 5601:localhost:5601 Chairman.Professor-Doctor@gabbagool.cs.usm.edu



"""


from flask import Flask, request, jsonify
from backend.admin.opensearch_client import OpenSearchClient
import configparser
import os

# Initialize the Flask application
app = Flask(__name__)

# Configuration for the OpenSearch connection
config_file = os.path.join(os.path.dirname(__file__), '../config.ini')
model_path = os.path.join(os.path.dirname(__file__), 'arq1thru3-finetuned-all-mpnet-jul-27')

OS_HOST = "localhost"
OS_PORT = 9200

config = configparser.ConfigParser()
config.read(config_file)
OS_USERNAME = config.get('OpenSearch', 'username')
OS_PASSWORD = config.get('OpenSearch', 'password')
# auth = (OS_USERNAME, OS_PASSWORD)

# Initialize the OpenSearch client
try:
    os_client = OpenSearchClient(OS_HOST, OS_PORT, OS_USERNAME, OS_PASSWORD)
except Exception as e:
    # If the connection fails, we log the error and exit
    app.logger.error(f"Failed to connect to OpenSearch: {e}")
    os_client = None

# Route to check the health of the OpenSearch cluster


# @app.route('/health', methods=['GET'])
# def health_check():
#     if not os_client:
#         return jsonify({"status": "error", "message": "OpenSearch client not initialized"}), 500

#     if os_client.check_health():
#         return jsonify({"status": "ok"})
#     else:
#         return jsonify({"status": "error", "message": "OpenSearch cluster is not healthy"}), 500

# # Route to create a new index in OpenSearch


# @app.route('/index', methods=['POST'])
# def create_index():
#     if not os_client:
#         return jsonify({"status": "error", "message": "OpenSearch client not initialized"}), 500

#     index_name = request.json.get('index_name')
#     if not index_name:
#         return jsonify({"status": "error", "message": "Index name is required"}), 400

#     if os_client.create_index(index_name):
#         return jsonify({"status": "ok", "message": f"Index '{index_name}' created successfully"})
#     else:
#         return jsonify({"status": "error", "message": f"Failed to create index '{index_name}'"}), 500

# # Route to add a new document to an index


# @app.route('/document', methods=['POST'])
# def add_document():
#     if not os_client:
#         return jsonify({"status": "error", "message": "OpenSearch client not initialized"}), 500

#     index_name = request.json.get('index_name')
#     document = request.json.get('document')

#     if not index_name or not document:
#         return jsonify({"status": "error", "message": "Index name and document are required"}), 400

#     doc_id = os_client.add_document(index_name, document)
#     if doc_id:
#         return jsonify({"status": "ok", "doc_id": doc_id})
#     else:
#         return jsonify({"status": "error", "message": "Failed to add document"}), 500

# # Route to search for documents in an index


# @app.route('/search', methods=['GET'])
# def search():
#     if not os_client:
#         return jsonify({"status": "error", "message": "OpenSearch client not initialized"}), 500

#     index_name = request.args.get('index_name')
#     query = request.args.get('q')

#     if not index_name or not query:
#         return jsonify({"status": "error", "message": "Index name and query are required"}), 400

#     results = os_client.search(index_name, query)
#     return jsonify(results)


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
