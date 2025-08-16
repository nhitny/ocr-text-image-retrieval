Dưới đây là bản cập nhật `README.md` hoàn chỉnh của bạn, đã **thêm phần dẫn link dữ liệu lưu trên Google Drive**:

---

````markdown
# 📘 OCR Text Image Retrieval - Hướng dẫn Cài đặt & Chạy hệ thống

Đồ án này là hệ thống tìm kiếm ảnh dựa trên văn bản OCR, hỗ trợ **BM25**, **Semantic** và **Hybrid Search**.

---

## ⚙️ Yêu cầu hệ thống

* Python 3.10+
* Conda
* `tmux` (để chạy nền Elasticsearch / API)
* Linux hoặc WSL2 (Ubuntu)

---

## 🚀 Cài đặt & chạy từng bước

### Bước 1: Tạo & kích hoạt môi trường Conda

```bash
conda create -n ocr python=3.10 -y
conda activate ocr
````

### Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Cài Elasticsearch 8.13.4

```bash
mkdir elasticsearch-dev
cd elasticsearch-dev
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.13.4-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.13.4-linux-x86_64.tar.gz --strip-components=1
rm elasticsearch-8.13.4-linux-x86_64.tar.gz
cd ..
```

### Bước 4: Chạy Elasticsearch

```bash
tmux new -s ocr
chmod +x scripts/start_elasticsearch.sh
bash scripts/start_elasticsearch.sh
```

> ⚠ Giữ tmux session này đang mở để Elasticsearch hoạt động.

### Bước 5: Build BM25

```bash
chmod +x scripts/build_elasticsearch.sh
bash scripts/build_elasticsearch.sh
```

Test:

```bash
curl 'http://localhost:9200/ocr_bm25/_search?q=text_bm25=công+văn&pretty'
```

### Bước 6: Build FAISS

```bash
chmod +x scripts/build_faiss.sh
bash scripts/build_faiss.sh
```

### Bước 7: Chạy API

```bash
tmux new -s api
python api/api.py
```

> Mặc định ở: [http://localhost:8880](http://localhost:8880)

### Bước 8: Chạy giao diện

```bash
streamlit run streamlit_app/dashboard.py
```

---

## 💾 Dữ liệu

Dữ liệu bao gồm ảnh và file OCR JSON được lưu tại:

🔗 [Google Drive - OCR Dataset](https://drive.google.com/file/d/1XG1hCsPwrJIo3NIwWomYSb3RrIOvl-Ul/view?usp=sharing)

> Hãy tải về và đặt vào thư mục `data/raw/` như sau:

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
├── streamlit_app/
│   └── dashboard.py
├── scripts/
│   ├── start_elasticsearch.sh
│   ├── build_elasticsearch.sh
│   ├── build_faiss.sh
├── data/
│   ├── raw/images/
│   └── raw/merged.json
└── requirements.txt
```

---

## 🧠 Giới thiệu Elasticsearch và FAISS

### Elasticsearch

* Dùng cho **tìm kiếm từ khóa** (BM25).
* Hiệu quả cao với từ chính xác: tên riêng, mã số, địa danh,...
* Dữ liệu được lưu dưới dạng chỉ mục trong `ocr_bm25`.

### FAISS

* Dùng cho **tìm kiếm ngữ nghĩa**.
* Ánh xạ nội dung OCR sang vector nhúng bằng mô hình embedding.
* Tìm ảnh có văn bản gần nghĩa với truy vấn, không cần trùng từ.

### Hybrid Search

* Kết hợp điểm BM25 và điểm cosine similarity từ FAISS:

  ```python
  hybrid_score = alpha * bm25_score + (1 - alpha) * semantic_score
  ```

* Giúp tăng độ chính xác trong các truy vấn phức tạp.

---

## 🧪 Demo API

```bash
curl "http://localhost:8880/search/bm25?query=công+văn&top_k=3"
curl "http://localhost:8880/search/semantic?query=CREATION&top_k=3"
curl "http://localhost:8880/search/hybrid?query=cải+cách&top_k=5&alpha=0.5"
```

