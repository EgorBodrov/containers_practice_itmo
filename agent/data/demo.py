from sentence_transformers import SentenceTransformer
from torch.cuda import is_available

from agent.data import Retriever


if __name__ == "__main__":
    encoder_model = SentenceTransformer(
        "deepvk/USER-bge-m3",
        device=0 if is_available() else -1
    )
    query = "Теория относительности кто изобрел?"
    print(Retriever(encoder_model=encoder_model).search(query, "scientists", 1))    
