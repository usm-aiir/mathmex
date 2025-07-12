### TSVs
The *.tsv files in the data directory contain qualitative data.
These files are comprised of data entries with a title, description, and source.

### NumPy Files
The *.npy files in the data directory contain the vector-representations of the descriptions, found in the associated *.tsv files. With the exception of YouTube data, which contains the vector-representation of the title.

### JSONL Files
The *.jsonl files are the combined data from the *.tsv and *.npy files. These are designed to be indexed into the OpenSearch database with ease.