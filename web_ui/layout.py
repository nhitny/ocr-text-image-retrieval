# web_ui/layout.py
import os
import requests
from flask import Blueprint, request, render_template_string

layout_bp = Blueprint("layout_ui", __name__)
API_BASE = os.getenv("API_BASE", "http://localhost:8880")  # server có /search_any & /images

HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>🔎 Mock OCR Webapp</title>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <style>
      body { font-family: system-ui, Arial; margin: 40px; background: #f7f7f9; }
      .card { max-width: 1000px; margin: auto; padding: 24px; background: #fff;
              border: 1px solid #ddd; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
      label { font-weight: 600; display:block; margin-top: 8px; }
      input[type=file], input[type=text], input[type=range] {
          width: 100%; padding: 10px; margin: 8px 0 16px;
          border: 1px solid #ccc; border-radius: 8px; background: #fff;
      }
      input[disabled] { background: #f0f0f0; color:#999; cursor:not-allowed; }
      button { padding: 12px 20px; border-radius: 10px; border: 0; background: #0b63ff;
               color: #fff; font-weight: 600; cursor: pointer; }
      button:hover { background: #084dcc; }
      .row { display: flex; gap: 24px; margin-top: 20px; justify-content: center; align-items: flex-start; flex-wrap: wrap; }
      .col { flex: 1; text-align: center; min-width: 260px; }
      img { max-width: 100%; height: auto; border: 1px solid #eee; border-radius: 10px; background:#fafafa; }
      .muted { color: #666; font-size: 13px; margin-top: 6px; white-space: pre-wrap; }
      .flash { background:#fffbdd; border:1px solid #ffe58f; padding:10px 12px; border-radius:10px; margin: 10px 0 14px; }
      .title { text-align:center; margin: 0 0 10px; font-size: 22px; }
      .inline { display:flex; align-items:center; gap:10px; }
      .inline span { min-width: 42px; text-align:right; font-variant-numeric: tabular-nums; }

      /* Button group cho phương pháp */
      .method-group { display:flex; gap:10px; margin:8px 0 16px; flex-wrap: wrap; }
      .method-btn {
        padding:10px 14px; border-radius:10px; border:1px solid #cfd3d7; background:#fff; cursor:pointer;
        font-weight:600;
        color:#0b63ff;   /* chữ xanh trên nền trắng */
      }
      .method-btn:hover { border-color:#0b63ff; }
      .method-btn.active {
        background:#0b63ff; color:#fff; border-color:#0b63ff;
      }

      /* Preview ảnh */
      .preview-wrap { display:none; margin-top: 6px; }
      .preview-box {
        display:flex; align-items:center; gap:12px; border:1px dashed #cfd3d7; border-radius:10px; padding:10px;
        background:#fbfcff;
      }
      .preview-thumb { width:90px; height:70px; object-fit:cover; border-radius:8px; border:1px solid #eee; }
      .preview-meta { font-size:13px; color:#555; }

      /* Loading overlay */
      .overlay {
        position: fixed; inset: 0; background: rgba(255,255,255,0.75);
        display: none; align-items: center; justify-content: center; z-index: 9999;
      }
      .spinner {
        width: 54px; height: 54px; border: 6px solid #d9e2ff; border-top-color: #0b63ff;
        border-radius: 50%; animation: spin 0.9s linear infinite;
      }
      .overlay-text { margin-top: 12px; text-align:center; color:#0b63ff; font-weight:600; }
      @keyframes spin { to { transform: rotate(360deg); } }
    </style>

    <script>
      function onTextInput(el) {
        const file = document.getElementById('image_input');
        const previewWrap = document.getElementById('preview_wrap');
        if (el.value.trim().length > 0) {
          file.disabled = true;
          if (previewWrap) { previewWrap.style.display = 'none'; }
        } else {
          file.disabled = false;
        }
      }

      function onFileInput(el) {
        const text = document.getElementById('text_input');
        const previewWrap = document.getElementById('preview_wrap');
        const previewImg  = document.getElementById('preview_img');
        const previewName = document.getElementById('preview_name');
        if (el.files && el.files.length > 0) {
          const f = el.files[0];
          text.disabled = true;
          text.value = "";
          if (window.FileReader) {
            const reader = new FileReader();
            reader.onload = function(e) {
              previewImg.src = e.target.result;
              previewName.textContent = f.name + " • " + Math.round(f.size/1024) + " KB";
              previewWrap.style.display = 'block';
            };
            reader.readAsDataURL(f);
          }
        } else {
          text.disabled = false;
          if (previewWrap) { previewWrap.style.display = 'none'; }
        }
      }

      function bindSliders() {
        const alpha = document.getElementById('alpha_range');
        const alphaVal = document.getElementById('alpha_val');
        if (alpha) alpha.oninput = () => alphaVal.innerText = alpha.value;

        const topk = document.getElementById('topk_range');
        const topkVal = document.getElementById('topk_val');
        if (topk) topk.oninput = () => topkVal.innerText = topk.value;
      }

      function onMethodSelect(btn) {
        document.querySelectorAll('.method-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const method = btn.getAttribute('data-method');
        document.getElementById('method_input').value = method;

        const alphaGroup = document.getElementById('alpha_group');
        if (alphaGroup) alphaGroup.style.display = (method === 'Hybrid') ? 'block' : 'none';
      }

      function onFormSubmit() {
        const overlay = document.getElementById('overlay');
        const submitBtn = document.getElementById('submit_btn');
        if (overlay) overlay.style.display = 'flex';
        if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "Đang xử lý..."; }
        return true;
      }

      window.addEventListener('DOMContentLoaded', bindSliders);
    </script>
  </head>
  <body>
    <div id="overlay" class="overlay">
      <div style="display:flex; flex-direction:column; align-items:center;">
        <div class="spinner"></div>
        <div class="overlay-text">Hệ thống đang tiến hành tìm kiếm...</div>
      </div>
    </div>

    <div class="card">
      <h2 class="title">🔎 Mock OCR Webapp</h2>

      <form method="post" enctype="multipart/form-data" onsubmit="return onFormSubmit()">
        <!-- Upload ảnh -->
        <label>Chọn ảnh đầu vào (hoặc bỏ trống nếu chỉ nhập text):</label>
        <input id="image_input" type="file" name="image" accept="image/*"
               onchange="onFileInput(this)" {{ 'disabled' if text_locked else '' }}>
        <div id="preview_wrap" class="preview-wrap">
          <div class="preview-box">
            <img id="preview_img" class="preview-thumb" alt="preview">
            <div class="preview-meta">
              <div id="preview_name">Ảnh đã chọn</div>
            </div>
          </div>
        </div>

        <!-- Text query -->
        <label>Text query:</label>
        <input id="text_input" type="text" name="text" value="{{ text or '' }}"
               placeholder="Ví dụ: Thành phố Hồ Chí Minh..."
               oninput="onTextInput(this)" {{ 'disabled' if file_locked else '' }}>

        <!-- Phương pháp -->
        <label>Phương pháp:</label>
        <input id="method_input" type="hidden" name="method" value="{{ method or 'Hybrid' }}">
        <div class="method-group">
        <button type="button" class="method-btn {% if method=='BM25' %}active{% endif %}"   data-method="BM25"    onclick="onMethodSelect(this)">BM25</button>
        <button type="button" class="method-btn {% if method=='Semantic' %}active{% endif %}" data-method="Semantic" onclick="onMethodSelect(this)">Semantic</button>
        <button type="button" class="method-btn {% if method=='Hybrid' %}active{% endif %}" data-method="Hybrid"  onclick="onMethodSelect(this)">Hybrid</button>
          
        </div>

        <!-- Top K -->
        <label>Top K: <span id="topk_val">{{ top_k or 3 }}</span></label>
        <div class="inline">
          <input id="topk_range" style="flex:1" type="range" name="top_k"
                 min="1" max="48" step="1" value="{{ top_k or 3 }}">
        </div>

        <!-- Alpha chỉ khi Hybrid -->
        <div id="alpha_group" style="display: {% if method=='Hybrid' %}block{% else %}none{% endif %};">
          <label>Alpha (Hybrid): <span id="alpha_val">{{ alpha or 0.5 }}</span></label>
          <div class="inline">
            <input id="alpha_range" style="flex:1" type="range" name="alpha"
                   min="0" max="1" step="0.05" value="{{ alpha or 0.5 }}">
          </div>
        </div>

        <div style="text-align:center; margin-top:10px;">
          <button id="submit_btn" type="submit">Tìm kiếm</button>
        </div>
      </form>

      {% if flash_msg %}
        <div class="flash">{{ flash_msg }}</div>
      {% endif %}

      {% if hits %}
        <div class="row">
          {% for h in hits %}
            {% set fname = (h.image_path or h.image or h.filename or '')|basename %}
            {% set imgsrc = h.image_url or (api_base ~ '/images/' ~ fname) %}
            <div class="col">
              <img src="{{ imgsrc }}" alt="img">
              {% if h.ocr_text or h.text %}
                <div class="muted">{{ (h.ocr_text or h.text)[:120] }}</div>
              {% endif %}
            </div>
          {% endfor %}
        </div>
      {% endif %}
    </div>
  </body>
</html>
"""

def _basename(path: str) -> str:
    try:
        return os.path.basename(path or "")
    except Exception:
        return path or ""

layout_bp.add_app_template_filter(_basename, "basename")

@layout_bp.route("/", methods=["GET", "POST"])
def home():
    hits = None
    flash_msg = None

    text   = request.form.get("text") if request.method == "POST" else ""
    method = request.form.get("method") if request.method == "POST" else "BM25"

    try:
        top_k = int(request.form.get("top_k", 3))
    except Exception:
        top_k = 3

    try:
        alpha = float(request.form.get("alpha", 0.5))
    except Exception:
        alpha = 0.5

    file_locked = False
    text_locked = False

    if request.method == "POST":
        files = {}
        data  = {"method": method, "top_k": str(top_k)}
        if method == "Hybrid":
            data["alpha"] = str(alpha)

        if text and text.strip():
            data["text"] = text.strip()
            file_locked = True
        else:
            img = request.files.get("image")
            if img and img.filename:
                files["image"] = (img.filename, img.stream, img.mimetype or "application/octet-stream")
                text_locked = True
            else:
                flash_msg = "Vui lòng nhập text hoặc chọn ảnh."

        if files or ("text" in data):
            try:
                resp = requests.post(f"{API_BASE}/search_any", data=data, files=files or None, timeout=180)
                resp.raise_for_status()
                hits = resp.json()
            except Exception as e:
                flash_msg = f"Lỗi gọi API: {e}"

    return render_template_string(
        HTML,
        hits=hits,
        flash_msg=flash_msg,
        text=text,
        method=method,
        top_k=top_k,
        alpha=alpha,
        api_base=API_BASE,
        file_locked=file_locked,
        text_locked=text_locked,
    )
