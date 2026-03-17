import os
from dotenv import load_dotenv

load_dotenv()
os.getenv("OPENAI_API_KEY")
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "email_assistant_memory")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")