from typing import List, Union
from pathlib import Path
from tqdm import tqdm

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models



class Retriever:
    def __init__(self, encoder_model: SentenceTransformer, host: str = None, port: str = None, url: str = None) -> None:
        self._encoder = encoder_model

        if host and port:
            self._client = QdrantClient(host, port=port)
        elif url:
            self._client = QdrantClient(url=url)
        else:
            save_data_path = Path(__file__).parent.resolve() / "qdrant_db"
            self._client = QdrantClient(path=save_data_path)
    
    def init_database(self, path_to_data: Path | str, collection_name: str = "scientists"):
        with open(path_to_data, "r+", encoding="utf-8") as file:
            data = [x.strip() for x in file.readlines()]
        
        embeddings = self._encoder.encode(data)
        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=len(embeddings[0]),
                distance=models.Distance.COSINE
            ),
        )
        for idx, row in tqdm(enumerate(data)):
            self._client.upsert(
                collection_name=collection_name,
                points=[models.PointStruct(id=idx, vector=embeddings[idx], payload={"text": row})]
            )

    def search(self, query: str, collection_name: str, topk: int = 3):
        embedding = self._encoder.encode(query)
        results = self._client.search(
            collection_name,
            embedding,
            limit=topk,
        )
        return results