from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, losses, util, models, evaluation
from utils.topic_reader import TopicReader
import csv
from bs4 import BeautifulSoup
from utils.post_parser_record import PostParserRecord
from sklearn.metrics import accuracy_score
import torch
import math
from torch.utils.data import DataLoader


def read_qrel_file(file_path):
    # Reading the ARQMath task 1 qrel file
    dic_topic_id_answer_id_relevance = {}
    with open(file_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            topic_id = row[0]
            answer_id = int(row[2])
            relevance_score = int(row[3])
            if topic_id in dic_topic_id_answer_id_relevance:
                dic_topic_id_answer_id_relevance[topic_id][answer_id] = relevance_score
            else:
                dic_topic_id_answer_id_relevance[topic_id] = {answer_id: relevance_score}
    return dic_topic_id_answer_id_relevance


# Uses the posts file, topic file(s) and qrel file(s) to build our training and evaluation sets.
def process_data(topic_reader, dic_qrel, val_dic_qrel, post_reader):
    train_samples = []
    evaluator_samples_1 = []
    evaluator_samples_2 = []
    evaluator_samples_score = []

    # Build Training set
    for topic_id in topic_reader.map_topics:
        # If the id is irrelevant, skip it
        if topic_id not in dic_qrel and topic_id not in val_dic_qrel:
            continue

        topic = topic_reader.map_topics[topic_id]
        question = topic.title.strip() + " " + topic.question
        question = BeautifulSoup(question, "lxml").text
        # question = question.replace("$", "")

        dic_answer_id = dic_qrel.get(topic_id, {})
        val_dic_answer_id = val_dic_qrel.get(topic_id, {})

        pos_samples = []
        neg_samples = []

        for answer_id in dic_answer_id:
            score = dic_answer_id[answer_id]
            if answer_id not in post_reader.map_just_answers:
                continue
            answer = post_reader.map_just_answers[answer_id]
            answer = BeautifulSoup(answer.body, "lxml").text
            # answer = answer.replace("$", "")

            if score > 1:
                pos_samples.append(InputExample(texts=[question, answer], label=1.0))
            else:
                neg_samples.append(InputExample(texts=[question, answer], label=0.0))

        pos_length = len(pos_samples)
        neg_length = len(neg_samples)

        # Use equal distribution of negative and positive samples, found no improvement from using more negatives
        # Drastically reduces training time as well

        if neg_length < pos_length:
            new_neg_samples = neg_samples
        else:
            new_neg_samples = neg_samples[:pos_length]

        train_samples.extend(pos_samples)
        train_samples.extend(new_neg_samples)

        # Build Validation set
        for answer_id in val_dic_answer_id:
            score = val_dic_answer_id[answer_id]
            if answer_id not in post_reader.map_just_answers:
                continue
            answer = post_reader.map_just_answers[answer_id]
            answer = BeautifulSoup(answer.body, "lxml").text
            answer = answer.replace("$", "")

            if score > 1:
                label = 1.0
            elif score == 1:
                label = 0.5
            else:
                label = 0.0

            evaluator_samples_1.append(question)
            evaluator_samples_2.append(answer)
            evaluator_samples_score.append(label)

    return train_samples, evaluator_samples_1, evaluator_samples_2, evaluator_samples_score


from itertools import islice
import random


def shuffle_dict(d):
    keys = list(d.keys())
    random.shuffle(keys)
    return {key: d[key] for key in keys}


def split_train_validation(qrels, ratio=0.9):
    # Using items() + len() + list slicing
    # Split dictionary by half
    n = len(qrels)
    n_split = int(n * ratio)
    qrels = shuffle_dict(qrels)
    train = dict(islice(qrels.items(), n_split))
    validation = dict(islice(qrels.items(), n_split, None))

    return train, validation


def train(model,
          output_path:str,
          num_epochs:int=10,
          batch_size:int=64):
    # Reading the topic files
    topic_reader = TopicReader("./data/Topics_Task1_2020.xml")
    topic_reader.map_topics.update(TopicReader("./data/Topics_Task1_2021.xml").map_topics)
    # Reading the qrel files
    qrels = read_qrel_file("./data/task1_2021.tsv")
    qrels.update(read_qrel_file("./data/task1_2020.tsv"))
    train_dic_qrel, val_dic_qrel = split_train_validation(qrels, ratio=0.95)

    # Reading the post XML file (takes time)
    post_reader = PostParserRecord("./data/Posts.V1.3.xml")

    # train_dic_qrel = read_qrel_file("qrels/final_train_qrel")
    # val_dic_qrel = read_qrel_file("qrels/final_val_qrel")

    # Creating train and val dataset
    train_samples, evaluator_samples_1, evaluator_samples_2, evaluator_samples_score = process_data(
        topic_reader, train_dic_qrel, val_dic_qrel, post_reader)

    train_dataset = SentencesDataset(train_samples, model=model)
    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size)
    train_loss = losses.CosineSimilarityLoss(model=model)

    evaluator = evaluation.EmbeddingSimilarityEvaluator(evaluator_samples_1, evaluator_samples_2,
                                                        evaluator_samples_score, write_csv="evaluation-epoch.csv")


    # add evaluator to the model fit function
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=num_epochs,
        warmup_steps= math.ceil(len(train_dataloader) * num_epochs * 0.1),
        use_amp=True,
        save_best_model=True,
        show_progress_bar=True,
        output_path=output_path
    )


def main():
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    model.max_seq_length = 512
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)
    model.to(device)

    train(model,
          num_epochs=10,
          batch_size=16,
          output_path="./models/arq-all-mpnet")


if __name__ == '__main__':
    main()