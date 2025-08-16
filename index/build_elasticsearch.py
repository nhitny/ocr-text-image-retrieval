
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from config.config import MERGED_JSON, ES_HOST


import json
import re
import unicodedata
from elasticsearch import Elasticsearch, helpers


def normalize_text(text):
    """Chuẩn hóa unicode và loại bỏ khoảng trắng dư thừa."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()

def connect_elasticsearch():
    """Kết nối tới Elasticsearch, kiểm tra kết nối."""
    es = Elasticsearch(ES_HOST)
    if not es.ping():
        raise ConnectionError(f"Không thể kết nối tới Elasticsearch tại {ES_HOST}")
    return es

def create_index(es, index_name):
    """Tạo mới chỉ mục Elasticsearch với analyzer đơn giản."""
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Đã xóa chỉ mục cũ: {index_name}")

    mappings = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "vn_analyzer": {
                        "type": "standard",
                        "stopwords": "_none_"
                    }
                }
            },
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "image_path": {"type": "keyword"},
                "dataset": {"type": "keyword"},
                "text_bm25": {
                    "type": "text",
                    "analyzer": "vn_analyzer"
                }
            }
        }
    }

    es.indices.create(index=index_name, body=mappings)
    print(f"Đã tạo chỉ mục mới: {index_name}")

def index_documents(es, index_name, json_path):
    """Nạp dữ liệu từ JSON và index vào Elasticsearch."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    actions = []
    for doc in data:
        actions.append({
            "_index": index_name,
            "_id": doc["image"],
            "_source": {
                "image_path": doc["image"],
                "dataset": doc.get("dataset", "unknown"),
                "text_bm25": normalize_text(doc["text"])
            }
        })

    helpers.bulk(es, actions)
    print(f"Đã index {len(actions)} tài liệu vào: {index_name}")

def main():
    index_name = "ocr_bm25"
    es = connect_elasticsearch()
    create_index(es, index_name)
    index_documents(es, index_name, MERGED_JSON)

if __name__ == "__main__":
    main()
