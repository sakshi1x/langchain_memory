from memory.qdrant_store import QdrantStore
from config.settings import QDRANT_PATH, COLLECTION_NAME, EMBEDDING_MODEL
import uuid

class MemoryManager:
    def __init__(self):
        self.store = QdrantStore(
            path=QDRANT_PATH,
            collection_name=COLLECTION_NAME,
            embedding_model=EMBEDDING_MODEL,
        )

    def save_example(self, namespace, data):
        key = str(uuid.uuid4())
        self.store.put(namespace, key, data)

    def retrieve_examples(self, namespace, query, limit=3):
        results = self.store.search(namespace, query, limit)
        # print(f"[DEBUG] Retrieved from memory: {results}")  # Log memory retrieval
        return results

    def close(self):
        if hasattr(self.store, 'client'):
            self.store.client.close()