import ranx

# Change this for your model's results, generated from evaluation.py
RUN_PATH = "./data/base_results.tsv"

print( ranx.evaluate(
    qrels=ranx.Qrels.from_file("./data/task1_2022.tsv", kind="trec"),
    run=ranx.Run.from_file(RUN_PATH, kind="trec"),
    metrics=["mrr@5", "precision@5"]
))