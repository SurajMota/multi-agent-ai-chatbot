# backend/app/services/pinecone_service.py

import os
from pinecone import Pinecone, ServerlessSpec
from server.logger import log

# Load ENV
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

# Your Index Name
INDEX_NAME = "suraj-chat-rag-index"

# ---------------------------------------
# 1. Create Pinecone Client
# ---------------------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)

# ---------------------------------------
# 2. Ensure Index Exists
# ---------------------------------------
def ensure_index():
    existing = [idx["name"] for idx in pc.list_indexes()]

    if INDEX_NAME not in existing:
        log.info(f"Creating Pinecone index → {INDEX_NAME}")

        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,          # MUST match your embedding model
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=PINECONE_ENV
            )
        )

ensure_index()

# ---------------------------------------
# 3. Get the Index Instance (Singleton)
# ---------------------------------------
_index = pc.Index(INDEX_NAME)

def get_pinecone_index():
    """
    Return initialized Pinecone index.
    Used by rag_query.py and KnowledgeAgent.
    """
    return _index
