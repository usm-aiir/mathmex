#!/bin/bash
# Process a data source: generate vectors, then JSONL. Optionally index to OpenSearch.
# Run from project root.
#
# Usage: bin/process.sh SOURCE TSV_FILE [--index]
#   e.g. bin/process.sh wikipedia final_wikipedia.tsv
#   e.g. bin/process.sh wikipedia final_wikipedia.tsv --index
#
# Outputs data/jsonl/mathmex_<source>.jsonl ready for bulk indexing.

set -e
cd "$(dirname "$0")/.."

if [ $# -lt 2 ]; then
    echo "Usage: $0 SOURCE TSV_FILE [--index]"
    echo "  e.g. $0 wikipedia final_wikipedia.tsv"
    echo "  e.g. $0 wikipedia final_wikipedia.tsv --index"
    echo ""
    echo "TSV_FILE should exist in data/tsvs/"
    exit 1
fi

SOURCE="$1"
TSV="$2"
DO_INDEX=false
[ "${3:-}" = "--index" ] && DO_INDEX=true

JSONL="data/jsonl/mathmex_${SOURCE}.jsonl"

echo "=========================================="
echo "Data source: $SOURCE"
echo "TSV: data/tsvs/$TSV"
echo "=========================================="
echo ""

echo "[1/2] Generating vectors..."
python apps/data-processing/generate_vectors.py "$SOURCE" "$TSV"
echo ""

echo "[2/2] Generating JSONL..."
python apps/data-processing/generate_jsonl.py "$SOURCE" "$TSV"
echo ""

if [ "$DO_INDEX" = true ]; then
    echo "[3/3] Indexing to OpenSearch..."
    python apps/opensearch/scripts/bulk_index.py "$SOURCE"
    echo ""
fi

echo "=========================================="
echo "Done. Data ready for indexing."
echo ""
echo "  JSONL: $JSONL"
echo ""
if [ "$DO_INDEX" = false ]; then
    echo "  Index with: python apps/opensearch/scripts/bulk_index.py $SOURCE"
fi
echo "=========================================="
