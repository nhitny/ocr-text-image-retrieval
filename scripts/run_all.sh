#!/bin/bash

echo "Chạy Elasticsearch trong tmux 'ocr'..."
tmux new-session -d -s ocr "bash scripts/start_elasticsearch.sh"
sleep 10

echo "Build chỉ mục BM25..."
bash scripts/build_elasticsearch.sh

echo "Build chỉ mục FAISS..."
bash scripts/build_faiss.sh

echo "Chạy Flask API trong tmux 'api'..."
tmux new-session -d -s api "python api/api.py"

echo "Khởi chạy Streamlit dashboard..."
streamlit run streamlit_app/dashboard.py
