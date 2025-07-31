from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, losses, util, models
from sentence_transformers.util import semantic_search
from utils.topic_reader import TopicReader
import csv
from bs4 import BeautifulSoup
from utils.post_parser_record import PostParserRecord
import torch
from tqdm import tqdm

def read_qrel_file(file_path):
    # Reading the ARQMath task 1 qrel file
    question_answer_pairs = {}
    with open(file_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            topic_id = row[0]
            answer_id = int(row[2])
            if topic_id not in question_answer_pairs:
                question_answer_pairs[topic_id] = []
            question_answer_pairs[topic_id].append(answer_id)
    cnt = sum(len(v) for v in question_answer_pairs.values())
    print(cnt)
    return question_answer_pairs


# SET THIS TO THE SAME PATH AS IN TRAINING
model = SentenceTransformer('./models/arq-all-mpnet')

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
model.to(device)

# Reading the post XML file (takes time)
post_reader = PostParserRecord("./data/Posts.V1.3.xml")

# Reading the topic files
topic_reader_test = TopicReader("./data/Topics_Task1_2022.xml")

# Reading the qrel files
question_answer_pairs = read_qrel_file("./data/task1_2022.tsv")

model.eval()

####
#### RENAME THIS RESULT FILE CORRECTLY -- later you need this file for evaluation of your model
####
tsv_writer = csv.writer(open('data/base_results.tsv', 'w', newline=''), delimiter='\t')

for topic_id in tqdm(question_answer_pairs, desc="Testing"):
    topic = topic_reader_test.map_topics[topic_id]
    question = topic.title.strip() + " " + topic.question
    question = BeautifulSoup(question, "lxml").text
    question = question.replace("$", "")
    answers_texts = []
    answer_ids = question_answer_pairs[topic_id]
    for answer_id in answer_ids:
        if answer_id not in post_reader.map_just_answers:
            continue
        answer = post_reader.map_just_answers[answer_id]
        answer = BeautifulSoup(answer.body, "lxml").text
        answer = answer.replace("$", "")
        answers_texts.append(answer)

    question_embedding = model.encode([question]*len(answers_texts), convert_to_tensor=True)
    answer_embeddings = model.encode(answers_texts, convert_to_tensor=True)

    # Only save top 100 results
    top_k = 100

    # Compute semantic search using the query and answer embeddings
    results = util.semantic_search(question_embedding, answer_embeddings, top_k=top_k)

    # Retrieve the top-k matching entries for the question
    top_k_entries = results[0][:top_k]

    for rank, entry in enumerate(top_k_entries):
        answer_id = answer_ids[entry['corpus_id']]
        cosine_score = entry['score']

        # Write the ranking results to the TSV file
        tsv_writer.writerow([topic_id, 'Q0', answer_id, rank+1, float(cosine_score), 'STANDARD'])