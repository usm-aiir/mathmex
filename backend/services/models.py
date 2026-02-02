from flask import current_app
from sentence_transformers import SentenceTransformer
import configparser
import os
import sys
from transformers import pipeline
sys.path.append(os.path.expanduser("../formula-search"))
from tangent_cft_back_end import TangentCFTBackEnd
from Embedding_Preprocessing.encoder_tuple_level import TupleTokenizationMode


embedding_model = None
tangent_backend = None
generation_model = None

def load_models():
    global embedding_model, tangent_backend, generation_model

    if embedding_model is None:
        config = configparser.ConfigParser()
        config.read(os.getenv("BACKEND_CONFIG", "config.ini"))
        embedding_model = SentenceTransformer(
            config.get("general", "model")
        )

    if tangent_backend is None:
        tangent_backend = TangentCFTBackEnd(
            config_file="../../formula-search/Configuration/config/config_1",
            path_data_set="../../formula-search/ARQMathDataset",
            is_wiki=False,
            streaming=True,
            read_slt=True,
            queries_directory_path="../../ARQMathQueries/test_SLT.tsv",
            faiss=True
        )

        tangent_backend.load_model(
            map_file_path="data/tsvs/TangentCFT/slt_encoder.tsv",
            model_file_path="data/vectors/TangentCFT/slt_model",
            embedding_type=TupleTokenizationMode(3),
            ignore_full_relative_path=True,
            tokenize_all=False,
            tokenize_number=True
        )

    # uncommment when we want to use the generation model
    # if generation_model is None:
    #     generation_model = pipeline("text-generation", model="mistralai/Mistral-7B-v0.3")

    print("Models are loaded")

# Note these are just passing references, not copies. So this is efficient versus reloading models in multiple places.
def get_embedding_model():
    return embedding_model

def get_tangent_backend():
    return tangent_backend

def get_generation_model():
    return generation_model