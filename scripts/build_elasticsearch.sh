#!/bin/bash

# Kích hoạt môi trường Conda tên "ocr"
eval "$(conda shell.bash hook)"
conda activate ocr

# Chạy script build chỉ mục Elasticsearch
python index/build_elasticsearch.py
