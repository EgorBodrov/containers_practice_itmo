from pathlib import Path
import argparse

from sentence_transformers import SentenceTransformer
from torch.cuda import is_available

from agent.data import Retriever


parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default=None)
parser.add_argument("--port", type=int, default=None)
parser.add_argument("--url", type=str, default=None)

if __name__ == "__main__":
    args = parser.parse_args()
    host = args.host
    port = args.port
    url = args.url

    path = Path(__file__).parent.resolve() / "data_raw.txt"

    encoder_model = SentenceTransformer(
        "deepvk/USER-bge-m3",
        device="cuda" if is_available() else "cpu"
    )
    Retriever(encoder_model=encoder_model, host=host, port=port, url=url).init_database(path_to_data=path)
