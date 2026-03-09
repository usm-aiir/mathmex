from sentence_transformers import SentenceTransformer
import os
import sys

from paths import ROOT, FORMULA_SEARCH_PATH, setup_formula_search_imports
from config_loader import get_config

embedding_model = None
tangent_backend = None
generation_model = None

def load_models():
    global embedding_model, tangent_backend, generation_model

    if embedding_model is None:
        config = get_config()
        model_path = os.path.expanduser(config.get("general", "model"))
        embedding_model = SentenceTransformer(model_path)

    if tangent_backend is None and FORMULA_SEARCH_PATH.exists():
        try:
            setup_formula_search_imports()
            fs = str(FORMULA_SEARCH_PATH)
            from tangent_cft_back_end import TangentCFTBackEnd
            from Embedding_Preprocessing.encoder_tuple_level import TupleTokenizationMode
            tangent_backend = TangentCFTBackEnd(
                config_file=f"{fs}/Configuration/config/config_1",
                path_data_set=f"{fs}/ARQMathDataset",
                is_wiki=False,
                streaming=True,
                read_slt=True,
                queries_directory_path=str(ROOT / "ARQMathQueries" / "test_SLT.tsv"),
                faiss=True
            )
            tangent_backend.load_model(
                map_file_path=f"{fs}/Embedding_Preprocessing/slt_encoder.tsv",
                model_file_path=f"{fs}/slt_model",
                embedding_type=TupleTokenizationMode(3),
                ignore_full_relative_path=True,
                tokenize_all=False,
                tokenize_number=True
            )
        except Exception:
            tangent_backend = None

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