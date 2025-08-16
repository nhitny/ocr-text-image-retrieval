import os
import re
import unicodedata
from elasticsearch import Elasticsearch

# Kết nối Elasticsearch
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "ocr_bm25"

# Chuẩn hóa văn bản đầu vào
def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

# Tạo đường dẫn ảnh từ tên file
def to_image_url(filename: str) -> str:
    return f"http://localhost:8880/images/{filename}"

# Tìm kiếm bằng BM25, trả về danh sách kết quả có score chuẩn hóa
def search_bm25(query: str, top_k: int = 5):
    query = normalize_text(query)

    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "match": {
                    "text_bm25": query
                }
            }
        },
        size=top_k
    )

    max_score = response["hits"]["max_score"] or 1e-9
    results = []

    for hit in response["hits"]["hits"]:
        raw_path = hit["_source"]["image_path"]
        filename = os.path.basename(raw_path)
        raw_score = hit["_score"]
        norm_score = raw_score / max_score

        results.append({
            "image_path": to_image_url(filename),
            "text": hit["_source"]["text_bm25"],
            "score": norm_score,
            "raw_score": raw_score
        })

    return results

# Test tìm kiếm BM25
if __name__ == "__main__":
    sample_query = "Chuyện những người mang số 115. Sáng nay ngồi cà phê cô"
    top_k = 5

    print(f"\nBM25 Search for: \"{sample_query}\"\n")
    search_results = search_bm25(sample_query, top_k=top_k)

    for i, r in enumerate(search_results, 1):
        print(f"{i}. [normalized: {r['score']:.4f} | raw: {r['raw_score']:.4f}] {r['image_path']}")
        print(f"    Text: {r['text']}\n")
