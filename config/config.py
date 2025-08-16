import os
from dotenv import load_dotenv

load_dotenv()

IMAGE_DIR = os.getenv("IMAGE_DIR")
MERGED_JSON = os.getenv("JSON_DIR", os.path.join(IMAGE_DIR, "merged.json"))

INDEX_DIR = os.getenv("INDEX_DIR", "index")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", os.path.join(INDEX_DIR, "faiss", "faiss_index.bin"))
METADATA_PATH = os.getenv("METADATA_PATH", os.path.join(INDEX_DIR, "faiss", "metadata.pkl"))

MODEL_NAME = os.getenv("MODEL_NAME", "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")

os.environ["TRANSFORMERS_CACHE"] = os.getenv("TRANSFORMERS_CACHE", ".cache")
os.environ["HF_HOME"] = os.getenv("HF_HOME", ".cache")
os.environ["SENTENCE_TRANSFORMERS_HOME"] = os.getenv("SENTENCE_TRANSFORMERS_HOME", ".cache")

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
PORT = int(os.getenv("PORT", 8880))
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", f"http://localhost:{PORT}/images")

DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 5))
DEFAULT_ALPHA = float(os.getenv("DEFAULT_ALPHA", 0.5))
API_BASE = f"http://localhost:{PORT}"
