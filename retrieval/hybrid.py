from urllib.parse import urlparse
import os
import sys
import unicodedata
import re
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from config.config import FAISS_INDEX_PATH, METADATA_PATH

from retrieval.bm25 import search_bm25
from retrieval.semantic import search_semantic

def normalize_text(text: str) -> str:
    """Chuẩn hóa văn bản."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    return text.lower()

def normalize_scores(scores: list[float]) -> list[float]:
    """Chuẩn hóa điểm về khoảng [0, 1]."""
    scores = np.array(scores)
    if np.ptp(scores) == 0:
        return [1.0] * len(scores)
    return ((scores - scores.min()) / np.ptp(scores)).tolist()

def extract_filename(path: str) -> str:
    """Trích xuất tên file từ đường dẫn hoặc URL."""
    return os.path.basename(urlparse(path).path)

def rerank_bm25_faiss(query: str, top_k: int = 5, alpha: float = 0.5) -> list[dict]:
    """
    Kết hợp kết quả từ BM25 và FAISS bằng reranking tuyến tính.

    Args:
        query (str): Truy vấn tìm kiếm
        top_k (int): Số lượng kết quả cần trả về
        alpha (float): Trọng số của BM25 (1-alpha là trọng số FAISS)

    Returns:
        list[dict]: Danh sách kết quả reranked
    """
    query = normalize_text(query)

    bm25_results = search_bm25(query, top_k=top_k * 2)
    faiss_results = search_semantic(query, top_k=top_k * 2)

    bm25_map = {extract_filename(r["image_path"]): r for r in bm25_results}
    faiss_map = {extract_filename(r["image_path"]): r for r in faiss_results}
    all_keys = set(bm25_map) | set(faiss_map)

    combined = []
    for key in all_keys:
        bm25 = bm25_map.get(key, {})
        faiss = faiss_map.get(key, {})

        combined.append({
            "image_path": bm25.get("image_path") or faiss.get("image_path"),
            "text": bm25.get("text") or faiss.get("text"),
            "bm25_score": bm25.get("score", 0),
            "faiss_score": faiss.get("score", 0),
        })

    bm25_norm = normalize_scores([c["bm25_score"] for c in combined])
    faiss_norm = normalize_scores([c["faiss_score"] for c in combined])

    for i, c in enumerate(combined):
        c["score"] = alpha * bm25_norm[i] + (1 - alpha) * faiss_norm[i]

    return sorted(combined, key=lambda x: x["score"], reverse=True)[:top_k]

if __name__ == "__main__":
    query = "Và 115 đã trở thành số điện thoại"
    alpha = 0.6
    results = rerank_bm25_faiss(query, top_k=5, alpha=alpha)

    print(f"Hybrid search for: \"{query}\" (alpha={alpha})\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [score: {r['score']:.4f}] {r['image_path']}")
        print(f"    Text: {r['text']}\n")
