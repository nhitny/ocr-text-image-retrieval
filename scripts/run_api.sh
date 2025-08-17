#!/usr/bin/env bash
set -euo pipefail

# ==== Repo root (cha của scripts/) ====
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ==== Thông số cố định theo yêu cầu ====
CUDA_DEVICE=5
OCR_CACHE_DIR="${ROOT}/.cache"
# Thư mục model local bạn nói:
CACHE_MODEL_DIR="${ROOT}/.cache/models--erax--EraX-VL-7B-V1"

# Chọn snapshot mới nhất trong cache HF (đúng chuẩn Transformers)
if [ -d "${CACHE_MODEL_DIR}/snapshots" ]; then
  SNAP_DIR="$(ls -dt "${CACHE_MODEL_DIR}/snapshots"/*/ 2>/dev/null | head -n 1 || true)"
else
  SNAP_DIR=""
fi

# Nếu tìm được snapshot -> dùng đường dẫn local; nếu không -> dùng tên model trên HF
if [ -n "${SNAP_DIR}" ]; then
  OCR_MODEL_ID="${SNAP_DIR%/}"   # bỏ trailing slash
  echo "[info] Using local snapshot model: ${OCR_MODEL_ID}"
  export TRANSFORMERS_OFFLINE=1   # dùng offline nếu đã có đủ file
else
  OCR_MODEL_ID="erax/EraX-VL-7B-V1"
  echo "[warn] Snapshot not found at ${CACHE_MODEL_DIR}/snapshots, fallback to HF id: ${OCR_MODEL_ID}"
  # không bật OFFLINE để Transformers có thể tải nếu thiếu
fi

# ==== Export biến môi trường cho OCR runtime ====
export CUDA_VISIBLE_DEVICES="${CUDA_DEVICE}"
export OCR_MODEL_ID OCR_CACHE_DIR
# Bật 4-bit nếu muốn: export OCR_USE_4BIT=1

# In PORT hiện dùng (để biết URL)
python - <<PY || true
import sys
sys.path.append(r"${ROOT}")
try:
    from config.config import PORT
    print(f"[info] API will run at: http://0.0.0.0:{PORT}")
except Exception:
    print("[warn] Cannot read PORT from config.config, defaulting to 8880")
PY

echo "[info] CUDA_VISIBLE_DEVICES = ${CUDA_VISIBLE_DEVICES}"
echo "[info] OCR_MODEL_ID        = ${OCR_MODEL_ID}"
echo "[info] OCR_CACHE_DIR       = ${OCR_CACHE_DIR}"
echo "[info] Starting Flask API (package mode) from ${ROOT} ..."

# ==== Chạy API theo package mode (kiểu A) ====
PYTHONPATH="${ROOT}" python -m api.api

echo "[info] Flask API is running"