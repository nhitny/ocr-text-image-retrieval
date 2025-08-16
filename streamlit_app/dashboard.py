import streamlit as st
import requests
import unicodedata
import re
import sys
import os


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from config.config import API_BASE, DEFAULT_TOP_K

ENDPOINTS = {
    "BM25": f"{API_BASE}/search/bm25",
    "Semantic": f"{API_BASE}/search/semantic",
    "Hybrid": f"{API_BASE}/search/hybrid",
}

def normalize(text: str) -> str:
    """Chuẩn hóa văn bản đầu vào."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip().lower()

def query_api(method: str, query: str, top_k: int):
    """Gửi truy vấn tới API và lấy kết quả."""
    try:
        res = requests.get(ENDPOINTS[method], params={"query": query, "top_k": top_k})
        res.raise_for_status()
        data = res.json()
        return data.get("results", data) if isinstance(data, dict) else data
    except Exception as e:
        st.error(f"Lỗi khi gọi API: {e}")
        return []

def render_results(results, score_threshold: float, cols_per_row: int = 3):
    """Hiển thị kết quả dạng lưới sau khi lọc theo score."""
    filtered = [r for r in results if r.get("score", 1.0) >= score_threshold]
    if not filtered:
        st.warning("Không có kết quả vượt ngưỡng.")
        return

    st.subheader("📸 Kết quả tìm kiếm:")
    cols = st.columns(cols_per_row)
    for i, r in enumerate(filtered):
        with cols[i % cols_per_row]:
            if "score" in r:
                st.markdown(f"**Score: {r['score']:.4f}**")
            st.image(r["image_path"], use_container_width=True)
            st.markdown(f"**{r.get('text', '')}**")

st.set_page_config(layout="wide")
st.title("🔍 OCR Image Search")

query = st.text_input("Nhập truy vấn:")
method = st.radio("Phương pháp tìm kiếm", list(ENDPOINTS.keys()))
top_k = st.slider("Top K", 1, 10, DEFAULT_TOP_K)
score_thresh = st.slider("Threshold", 0.0, 1.0, 0.0, 0.01)

if st.button("Tìm kiếm") and query:
    normalized = normalize(query)
    results = query_api(method, normalized, top_k)
    render_results(results, score_thresh)
