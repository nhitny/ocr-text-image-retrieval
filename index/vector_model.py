import re
import unicodedata
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Cấu hình thiết bị (ưu tiên GPU nếu có)
DEVICE = torch.device("cuda:5" if torch.cuda.is_available() else "cpu")

# Tên mô hình encode
MODEL_NAME = "keepitreal/vietnamese-sbert"

# Load SentenceTransformer
model = SentenceTransformer(MODEL_NAME, device=str(DEVICE))

def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản: chuẩn Unicode, gộp khoảng trắng.
    """
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def encode_texts(texts: list[str], normalize: bool = True, batch_size: int = 32) -> np.ndarray:
    """
    Mã hóa danh sách văn bản thành vector numpy.

    Args:
        texts (list of str): Danh sách văn bản cần encode
        normalize (bool): Có chuẩn hóa vector đầu ra không
        batch_size (int): Batch size khi encode

    Returns:
        np.ndarray: Ma trận embedding (num_texts, dim)
    """
    cleaned_texts = [normalize_text(t) for t in texts]
    embeddings = model.encode(
        cleaned_texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
    )
    return embeddings
