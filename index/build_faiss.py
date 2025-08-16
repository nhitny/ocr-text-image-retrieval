import os
import json
import pickle
import faiss
import sys
import re
import unicodedata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import MERGED_JSON, FAISS_INDEX_PATH, METADATA_PATH

from index.vector_model import encode_texts


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s.lower()


def load_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = load_json(MERGED_JSON)

    texts = []
    metadata = []

    for item in data:
        clean_text = normalize_text(item["text"])
        texts.append(clean_text)

        relative_image_path = os.path.normpath(os.path.join("data/raw", item["image"]))

        metadata.append({
            "image_path": relative_image_path,
            "dataset": item.get("dataset", "unknown") or "unknown",
            "text": clean_text,
        })

    print(f"Total texts to encode: {len(texts)}")

    vectors = encode_texts(texts)

    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"\nFAISS index saved: {len(vectors)} vectors → {FAISS_INDEX_PATH}")
    print("Vector shape:", vectors.shape)
    print("Example metadata:")
    print(json.dumps(metadata[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
