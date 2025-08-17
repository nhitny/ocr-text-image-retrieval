# 📘 OCR Text Image Retrieval

Đồ án này là hệ thống tìm kiếm ảnh dựa trên văn bản OCR, hỗ trợ **BM25**, **Semantic** và **Hybrid Search**.

---

## ⚙️ Yêu cầu hệ thống

* Python 3.10+
* Conda
* `tmux` (để chạy nền Elasticsearch / API / Web UI)
* Linux hoặc WSL2 (Ubuntu)

---

## 🚀 Cài đặt & chạy từng bước

### 🔹 Bước 1: Tạo & kích hoạt môi trường Conda

```bash
conda create -n ocr python=3.10 -y
conda activate ocr
```

### 🔹 Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 🔹 Bước 3: Cài Elasticsearch 8.13.4

```bash
mkdir elasticsearch-dev
cd elasticsearch-dev
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.13.4-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.13.4-linux-x86_64.tar.gz --strip-components=1
rm elasticsearch-8.13.4-linux-x86_64.tar.gz
cd ..
```

---

## ▶️ Quy trình chạy hệ thống

### 1️⃣ Chạy Elasticsearch (bắt buộc, luôn chạy nền)

```bash
tmux new -s es
bash scripts/run_elasticsearch.sh
```

> Elasticsearch chạy ở `http://localhost:9200`

---

### 2️⃣ Build chỉ mục (chỉ chạy **lần đầu** hoặc khi thay đổi dataset)

```bash
bash scripts/build_elasticsearch.sh   # Tạo chỉ mục BM25
bash scripts/build_faiss.sh           # Tạo chỉ mục FAISS
```

Test Elasticsearch:

```bash
curl 'http://localhost:9200/ocr_bm25/_search?q=text_bm25=công+văn&pretty'
```

---

### 3️⃣ Chạy API backend

```bash
tmux new -s api
bash scripts/run_api.sh
```

> API chạy ở: [http://localhost:8880](http://localhost:8880)

Ví dụ gọi API:

```bash
curl "http://localhost:8880/search/bm25?query=công+văn&top_k=3"
curl "http://localhost:8880/search/semantic?query=CREATION&top_k=3"
curl "http://localhost:8880/search/hybrid?query=cải+cách&top_k=5&alpha=0.5"
```

---

### 4️⃣ Chạy Web UI (Flask giao diện)

```bash
tmux new -s web
python -m web_ui.layout
```

> Web UI chạy ở: [http://127.0.0.1:8889](http://127.0.0.1:8889)

Muốn mở cho máy khác trong LAN truy cập → sửa trong `web_ui/layout.py`:

```python
app.run(host="0.0.0.0", port=8889, debug=True)
```

---

## 💾 Dữ liệu

Dataset gồm ảnh + OCR JSON:

🔗 [Google Drive - OCR Dataset](https://drive.google.com/file/d/1XG1hCsPwrJIo3NIwWomYSb3RrIOvl-Ul/view?usp=sharing)

Giải nén và đặt vào:

```
data/
└── raw/
    ├── images/
    └── merged.json
```

---

## 📂 Cấu trúc thư mục

```
.
├── api/
│   └── api.py
├── config/
│   └── config.py
├── retrieval/
│   ├── bm25.py
│   ├── semantic.py
│   └── hybrid.py
├── web_ui/
│   └── layout.py         # Flask giao diện
├── streamlit_app/
│   └── dashboard.py      # Dashboard demo (streamlit)
├── scripts/
│   ├── run_elasticsearch.sh
│   ├── run_api.sh
│   ├── build_elasticsearch.sh
│   ├── build_faiss.sh
├── data/
│   ├── raw/images/
│   └── raw/merged.json
└── requirements.txt
```

---

## 🧠 Giới thiệu Elasticsearch và FAISS

### 🔹 Elasticsearch

* Dùng cho **tìm kiếm từ khóa** (BM25).
* Hiệu quả cao với từ chính xác: tên riêng, mã số, địa danh,...
* Chỉ mục lưu trong `ocr_bm25`.

### 🔹 FAISS

* Dùng cho **tìm kiếm ngữ nghĩa**.
* Ánh xạ OCR → embedding vector.
* Truy vấn không cần khớp từ chính xác.

### 🔹 Hybrid Search

Kết hợp điểm BM25 và FAISS:

```python
hybrid_score = alpha * bm25_score + (1 - alpha) * semantic_score
```

---

## 🧪 Demo API

```bash
curl "http://localhost:8880/search/bm25?query=công+văn&top_k=3"
curl "http://localhost:8880/search/semantic?query=CREATION&top_k=3"
curl "http://localhost:8880/search/hybrid?query=cải+cách&top_k=5&alpha=0.5"
```


