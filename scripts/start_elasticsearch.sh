#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate ocr

ES_DIR="./elasticsearch-dev"

export ES_JAVA_OPTS="-Xms1g -Xmx1g"

$ES_DIR/bin/elasticsearch \
  -E xpack.security.enabled=false \
  -E xpack.security.enrollment.enabled=false \
  -E xpack.security.http.ssl.enabled=false \
  -E discovery.type=single-node
