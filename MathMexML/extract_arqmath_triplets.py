"""
extract_arqmath_triplets.py

This script parses the ARQMath Posts XML file to extract question/answer pairs and
generates (question, positive answer, negative answer) triplets for contrastive learning.

Pipeline context:
- Reads ARQMathData/Posts.V1.3.xml to extract all questions and answers.
- For each question and its answers (positives), randomly selects a negative answer from another question.
- Saves the resulting triplets as a pickle file for use in model training.

Requirements:
- lxml
- tqdm
- ARQMathData/Posts.V1.3.xml (downloaded from the ARQMath dataset)

Usage:
1. Place Posts.V1.3.xml in the ARQMathData/ subfolder.
2. Run this script:
   python extract_arqmath_triplets.py

Outputs:
- Triplets saved as ARQMathData/arqmath_triplets.pkl
"""
from lxml import etree
import random
import pickle
from tqdm import tqdm
import os

# Path to your ARQMath Posts XML file
POSTS_PATH = os.path.join("ARQMathData", "Posts.V1.3.xml")
OUTPUT_PATH = os.path.join("ARQMathData", "arqmath_triplets.pkl")

# Parse posts.xml to extract questions and answers
print("Parsing posts...")
questions = {}
answers = {}

for event, elem in tqdm(etree.iterparse(POSTS_PATH, tag="row")):
    post_id = elem.get("Id")
    post_type = elem.get("PostTypeId")
    body = elem.get("Body")
    parent_id = elem.get("ParentId")
    if post_type == "1":  # Question
        questions[post_id] = body
    elif post_type == "2":  # Answer
        answers[post_id] = (body, parent_id)
    elem.clear()

# Build mapping: question_id -> list of answer_ids
q_to_a = {}
for aid, (body, qid) in answers.items():
    if qid not in q_to_a:
        q_to_a[qid] = []
    q_to_a[qid].append(aid)

# Build triplets: (question, positive answer, negative answer)
triplets = []
question_ids = list(questions.keys())
for qid, qbody in tqdm(questions.items()):
    pos_ids = q_to_a.get(qid, [])
    if len(pos_ids) < 1:
        continue
    for pos_id in pos_ids:
        pos_body = answers[pos_id][0]
        # Pick a random negative answer from another question
        neg_qid = random.choice([k for k in question_ids if k != qid and k in q_to_a])
        neg_id = random.choice(q_to_a[neg_qid])
        neg_body = answers[neg_id][0]
        triplets.append((qbody, pos_body, neg_body))

print(f"Extracted {len(triplets)} triplets.")

# Save triplets for reuse
with open(OUTPUT_PATH, "wb") as f:
    pickle.dump(triplets, f)
print(f"Triplets saved to {OUTPUT_PATH}.")