# services/tangent_cft.py
import os
import sys
_ROUTES_DIR = os.path.dirname(os.path.abspath(__file__))
_FORMULA_SEARCH_PATH = os.path.abspath(
    os.path.join(_ROUTES_DIR,  "..", "..", "..", "formula-search")
)
if _FORMULA_SEARCH_PATH not in sys.path:
    sys.path.insert(0, _FORMULA_SEARCH_PATH)

from tangent_cft_back_end import TangentCFTBackEnd

_backend = None   
def load_tangent_cft():
    global _backend
    if _backend is None:
        _backend = TangentCFTBackEnd(
            config_file="../../formula-search/Configuration/config/config_1",
            path_data_set="../../formula-search/ARQMathDataset",
            is_wiki=False,
            streaming=True,
            read_slt=True,
            queries_directory_path="../../ARQMathQueries/test_SLT.tsv",
            faiss=True
        )
        # Look into calling load model here
    return _backend

def get_tangent_cft_backend():
    if _backend is None:
        raise RuntimeError("TangentCFT backend not initialized")
    return _backend
