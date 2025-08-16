import os
import sys
from flask import Flask, request, jsonify, send_from_directory

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

from config.config import IMAGE_DIR


from retrieval.bm25 import search_bm25
from retrieval.semantic import search_semantic
from retrieval.hybrid import rerank_bm25_faiss
from config.config import IMAGE_DIR, PORT, DEFAULT_TOP_K, DEFAULT_ALPHA

app = Flask(__name__)

@app.route("/search/bm25")
def search_bm25_api():
    query = request.args.get("query", "")
    top_k = int(request.args.get("top_k", DEFAULT_TOP_K))
    return jsonify(search_bm25(query, top_k))

@app.route("/search/semantic")
def search_semantic_api():
    query = request.args.get("query", "")
    top_k = int(request.args.get("top_k", DEFAULT_TOP_K))
    return jsonify(search_semantic(query, top_k))

@app.route("/search/hybrid")
def search_hybrid_api():
    query = request.args.get("query", "")
    top_k = int(request.args.get("top_k", DEFAULT_TOP_K))
    alpha = float(request.args.get("alpha", DEFAULT_ALPHA))
    return jsonify(rerank_bm25_faiss(query, top_k, alpha))

@app.route("/images/<path:filename>")
def serve_image(filename):
    from flask import abort
    filename_only = os.path.basename(filename)
    abs_path = os.path.join(IMAGE_DIR, filename_only)

    print(f"Serving image: {filename_only}")
    print(f"From dir: {IMAGE_DIR}")
    print(f"Full path: {abs_path}")

    if not os.path.exists(abs_path):
        print(f"File does not exist: {abs_path}")
        return abort(404)

    return send_from_directory(IMAGE_DIR, filename_only)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
