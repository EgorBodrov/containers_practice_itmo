from pathlib import Path

from sentence_transformers import SentenceTransformer
from torch.cuda import is_available

from agent.data import Retriever


if __name__ == "__main__":
    path = Path(__file__).parent.resolve() / "data_raw.txt"

    encoder_model = SentenceTransformer(
        "deepvk/USER-bge-m3",
        device=0 if is_available() else -1
    )
    Retriever(encoder_model=encoder_model).init_database(path_to_data=path)
