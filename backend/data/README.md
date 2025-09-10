### Python Scripts
The Python scripts in this directory are for data-file generation

### TSVs
The *.tsv files in the data directory contain qualitative data.
These files are comprised of data entries with a title, description, and source.
These files do not contain a row for column names.

### NumPy Files
The *.npy files in the data directory contain the vector-representations of the descriptions, found in the associated *.tsv files. With the exception of YouTube data, which contains the vector-representation of the title.

### JSONL Files
The *.jsonl files are the combined data from the *.tsv and *.npy files. These are designed to be indexed into the OpenSearch database with ease. When generating JSONL files, do not forget to change the "media-type" value for the data being indexed. 
The appropriate value for each source can be found in the mapping at the top of the 'generate_jsonl.py' script.