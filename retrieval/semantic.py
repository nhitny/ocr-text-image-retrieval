import os
import sys
import re
import faiss
import pickle
import unicodedata
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import FAISS_INDEX_PATH, METADATA_PATH, IMAGE_BASE_URL
from index.vector_model import encode_texts


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s.replace("\n", " ")).strip()
    return s.lower()


def to_image_url(filename: str) -> str:
    return f"{IMAGE_BASE_URL}/{filename}"


_index = faiss.read_index(FAISS_INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    _metadata = pickle.load(f)


def search_semantic(query: str, top_k: int = 5):
    query = normalize_text(query)
    query_vector = encode_texts([query])[0].astype("float32")
    D, I = _index.search(np.array([query_vector], dtype='float32'), top_k)

    max_dist = D[0].max() if D[0].max() > 0 else 1e-5
    norm_scores = 1 - D[0] / max_dist

    results = []
    for idx, score in zip(I[0], norm_scores):
        item = _metadata[idx]
        filename = os.path.basename(item["image_path"])
        results.append({
            "image_path": to_image_url(filename),
            "text": item.get("text", ""),
            "score": float(score),
        })

    return results


if __name__ == "__main__":
    query = "KHÁI QUÁT VỀ BIỂN ĐẢO VIỆT NAM"
    results = search_semantic(query, top_k=5)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['image_path']} → {r['score']:.4f}")
        print(f"Text: {r['text']}")
