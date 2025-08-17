# webui/ocr_runtime.py
from __future__ import annotations
import os, io, threading
from typing import Optional, List, Dict, Any

# ====== Cấu hình ======
CACHE_DIR = "/workspace/nhitny/projects/ocr_text_image_retrieval_v2/.cache"
MODEL_ID  = os.environ.get("OCR_MODEL_ID", "erax/EraX-VL-7B-V1")
USE_4BIT  = os.environ.get("OCR_USE_4BIT", "0") in ("1", "true", "True")

os.makedirs(CACHE_DIR, exist_ok=True)
# ép transformers/hf dùng đúng cache này
os.environ["HF_HOME"] = CACHE_DIR
os.environ["HUGGINGFACE_HUB_CACHE"] = CACHE_DIR
os.environ["TRANSFORMERS_CACHE"] = CACHE_DIR

import torch
from PIL import Image
from transformers import (
    Qwen2VLForConditionalGeneration,
    AutoProcessor,
    BitsAndBytesConfig,
)

# ====== Prompt tiếng Việt ======
PROMPT_VI = (
    "Trích xuất TẤT CẢ chữ trong ảnh dưới dạng văn bản thuần (plain text). "
    "Giữ thứ tự dòng từ trái sang phải, trên xuống dưới. "
    "Không thêm mô tả, không giải thích, chỉ in ra phần văn bản."
)

# ====== Singleton loader (thread-safe) ======
_lock = threading.Lock()
_loaded = False
_model: Optional[Qwen2VLForConditionalGeneration] = None
_processor: Optional[AutoProcessor] = None

def _load_once():
    """Load model + processor một lần, ép cache_dir = CACHE_DIR"""
    global _loaded, _model, _processor
    if _loaded:
        return
    with _lock:
        if _loaded:
            return

        quant_cfg = None
        if USE_4BIT:
            quant_cfg = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
            )

        # luôn dùng cache_dir=CACHE_DIR
        _model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            device_map="auto",
            torch_dtype="auto",
            quantization_config=quant_cfg,
            cache_dir=CACHE_DIR,
        ).eval()

        _processor = AutoProcessor.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR)
        _loaded = True

def _build_messages(pil_img: Image.Image) -> List[Dict[str, Any]]:
    return [{
        "role": "user",
        "content": [
            {"type": "image", "image": pil_img},
            {"type": "text",  "text": PROMPT_VI},
        ],
    }]

@torch.inference_mode()
def run_ocr_pil(
    pil_img: Image.Image,
    max_new_tokens: int = 512,
    temperature: float = 0.0,
    do_sample: bool = False,
) -> str:
    """OCR từ PIL Image -> text"""
    _load_once()
    assert _model is not None and _processor is not None

    img = pil_img.convert("RGB")
    messages = _build_messages(img)

    prompt = _processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = _processor(text=prompt, images=[img], return_tensors="pt")

    for k, v in list(inputs.items()):
        if isinstance(v, torch.Tensor):
            inputs[k] = v.to(_model.device)

    generated = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=do_sample,
    )

    out_ids = generated[0, inputs["input_ids"].shape[1]:]
    text = _processor.decode(out_ids, skip_special_tokens=True).strip()
    return text

@torch.inference_mode()
def run_ocr(
    image_bytes: bytes,
    max_new_tokens: int = 512,
    temperature: float = 0.0,
    do_sample: bool = False,
) -> str:
    """OCR từ bytes ảnh -> text"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return run_ocr_pil(img, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=do_sample)

def warmup(sample_image_path: Optional[str] = None):
    """Load model sớm (nếu có ảnh mẫu thì OCR thử để init GPU)."""
    _load_once()
    if sample_image_path and os.path.exists(sample_image_path):
        with open(sample_image_path, "rb") as f:
            _ = run_ocr(f.read(), max_new_tokens=64)
