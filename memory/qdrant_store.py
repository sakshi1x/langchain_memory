from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
import uuid
from qdrant_client.models import Distance, VectorParams

class QdrantStore:
    def __init__(self, path, collection_name, embedding_model):
        self.client = QdrantClient(path=path)
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        # Check if the collection exists, and create it if not
        if not self._collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )

    def _collection_exists(self, collection_name):
        try:
            self.client.get_collection(collection_name)
            return True
        except ValueError:
            return False

    def put(self, namespace, key, value):
        text = str(value)
        metadata = {
            "namespace": "|".join(namespace),
            "key": key,
            "value": value,
        }
        self.vector_store.add_texts(
            texts=[text],
            metadatas=[metadata],
            ids=[key]
        )

    def search(self, namespace, query, limit=3):
        results = self.vector_store.similarity_search(query, k=limit)
        # print(f"[DEBUG] Memory search results: {results}")  # Log memory search
        return results