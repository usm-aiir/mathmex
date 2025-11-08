# MathMex Data Pipeline

This directory contains all scripts and data files used to generate, process, and prepare data for indexing into the MathMex OpenSearch Database.

---

## Python Scripts
The Python scripts in this directory are used for data generation and transformation, including:

* Creating vector representations of text.
* Combining raw data into a unified JSONL format ready for OpenSearch indexing.

## TSV Files (*.tsv)
These files contain qualitative data in the form of:
[title, description, url]

Note: TSV files do not include a header row.

Each file provides source-specific entries describing mathematical content.

## NumPy Files (*.npy)
These files store the vector representations of the text fields found in the corresponding TSVs:

These embeddings are used to enable semantic and ML-powered search on MathMex.

## JSONL Files (*.jsonl)
Each JSONL file combines the data from the matching .tsv and .npy files into a structured, line-delimited JSON format suitable for bulk ingestion into OpenSearch.
When generating JSONL files:

* Ensure the "media-type" field correctly matches the data source.
* The mapping of each source to its media-type can be found at the top of the generate_jsonl.py script.

---

# Data Generation Pipeline

1. Prepare Raw Data
   
    Begin by creating one or more *.tsv files containing mathematical content formatted as:
    title<TAB>description<TAB>url

2. Generate Vectors
   
    Run:
    python generate_vectors.py

    This will produce a user-specified *.npy file containing the vector embeddings of your text data.

3. Combine and Export

   Run:
   python generate_jsonl.py

   This script merges your .tsv and .npy data into a .jsonl file, ready for upload to the MathMex OpenSearch database.