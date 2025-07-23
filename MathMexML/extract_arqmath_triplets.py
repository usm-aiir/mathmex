"""
extract_arqmath_triplets.py

This script parses the ARQMath Posts XML file to extract question/answer pairs and
generates (question, positive answer, negative answer) triplets for contrastive learning.

Pipeline context:
- Reads ARQMathData/Posts.V1.3.xml to extract all questions and answers using DataReaderRecord.
- For each question and its answers (positives), randomly selects a negative answer from another question.
- Saves the resulting triplets as a pickle file for use in model training.

Requirements:
- tqdm
- ARQMathData/Posts.V1.3.xml (downloaded from the ARQMath dataset)
- ARQMathCode/post_reader_record.py (in ARQMathCode/ subfolder)

Usage:
1. Place Posts.V1.3.xml in the ARQMathData/ subfolder.
2. Ensure ARQMathCode/post_reader_record.py is in your project.
3. Run this script:
   python extract_arqmath_triplets.py

Outputs:
- Triplets saved as ARQMathData/arqmath_triplets.pkl
"""
import random
import pickle
from tqdm import tqdm
import os
from ARQMathCode.post_reader_record import DataReaderRecord

# Path to your ARQMath Posts XML file
OUTPUT_PATH = os.path.join("ARQMathData", "arqmath_triplets.pkl")

# Parse posts.xml to extract questions and answers
print("Parsing posts using DataReaderRecord...")
reader = DataReaderRecord("ARQMathData", version=".V1.3")

# Get questions and answers
questions = {str(q.Id): q.Body for q in reader.post_parser.map_questions.values()}
answers = {str(a.Id): (a.Body, str(a.ParentId)) for a in reader.post_parser.map_answers.values()}

# Build mapping: question_id -> list of answer_ids
q_to_a = {}
for aid, (body, qid) in answers.items():
    if qid not in q_to_a:
        q_to_a[qid] = []
    q_to_a[qid].append(aid)

# Build triplets: (question, positive answer, negative answer)
MAX_TRIPLETS = None  # Set to an integer for a quick test, or None for all
triplets = []
question_ids = list(questions.keys())
for qid, qbody in tqdm(questions.items(), desc="Building triplets"):
    pos_ids = q_to_a.get(qid, [])
    if len(pos_ids) < 1:
        continue
    for pos_id in pos_ids:
        if MAX_TRIPLETS is not None and len(triplets) >= MAX_TRIPLETS:
            break
        pos_body = answers[pos_id][0]
        # Pick a random negative answer from another question
        neg_candidates = [k for k in question_ids if k != qid and k in q_to_a]
        if not neg_candidates:
            continue
        neg_qid = random.choice(neg_candidates)
        neg_id = random.choice(q_to_a[neg_qid])
        neg_body = answers[neg_id][0]
        triplets.append((qbody, pos_body, neg_body))
    if MAX_TRIPLETS is not None and len(triplets) >= MAX_TRIPLETS:
        break

print(f"Extracted {len(triplets)} triplets.")

# Save triplets for reuse
with open(OUTPUT_PATH, "wb") as f:
    pickle.dump(triplets, f)