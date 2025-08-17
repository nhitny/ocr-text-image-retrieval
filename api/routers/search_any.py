from flask import Blueprint, request, jsonify, abort
import sys
from pathlib import Path

# Import OCR runtime (đúng thư mục web_ui)
sys.path.append(str(Path(__file__).resolve().parents[2] / "web_ui"))
from ocr_runtime import run_ocr

from retrieval.bm25 import search_bm25
from retrieval.semantic import search_semantic
from retrieval.hybrid import rerank_bm25_faiss

search_any_bp = Blueprint("search_any", __name__)


@search_any_bp.route("/search_any", methods=["POST"])
def search_any():
    """
    API hợp nhất: nhập text hoặc ảnh
    - Nếu có text: dùng trực tiếp
    - Nếu có ảnh: OCR -> text
    - Sau đó search bằng BM25 / Semantic / Hybrid
    """
    text = request.form.get("text", "").strip()
    file = request.files.get("image")
    method = request.form.get("method", "Hybrid")

    # Parse tham số an toàn
    try:
        top_k = int(request.form.get("top_k", 9))
    except Exception:
        top_k = 9
    try:
        alpha = float(request.form.get("alpha", 0.5))
    except Exception:
        alpha = 0.5

    # Lấy query text
    if text:
        query_text = text
    elif file:
        raw = file.read()
        if not raw:
            abort(400, "Empty image file")
        try:
            query_text = run_ocr(raw)
        except Exception as e:
            abort(500, f"OCR failed: {e}")
    else:
        abort(400, "Provide either text or image")

    # Search theo method
    if method == "BM25":
        hits = search_bm25(query_text, top_k)
    elif method == "Semantic":
        hits = search_semantic(query_text, top_k)
    else:  # Hybrid mặc định
        hits = rerank_bm25_faiss(query_text, top_k, alpha)

    return jsonify(hits)
