# backend/app/tools/upload_kb.py

import os
import pandas as pd
from server.logger import log
from app.core.llm import get_embedding_model
from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV") or "us-east-1"

INDEX_NAME = "suraj-chat-rag-index"

pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if missing
if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    )
    print(f"Created index: {INDEX_NAME}")

index = pc.Index(INDEX_NAME)


def load_kb():
    """Load knowledgebase sheet"""
    file_path = "app/data/knowledgebase.xlsx"
    #file_path = "app/data/Knowledgebase.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: {file_path}")

    df = pd.read_excel(file_path)

    # Choose correct column
    if {"question", "answer"}.issubset(df.columns):
        df["text"] = df["question"] + " - " + df["answer"]
    elif "text" in df.columns:
        pass
    else:
        raise ValueError("KB must contain columns: 'question'+'answer' OR 'text'")

    return df["text"].tolist()


async def upload_chunks():
    """Generate embeddings + upload to Pinecone"""
    texts = load_kb()
    embed_model = get_embedding_model()

    vectors = []

    for i, text in enumerate(texts):
        emb = await embed_model.aembed(text)
        vectors.append({
            "id": f"kb-{i}",
            "values": emb,
            "metadata": {"text": text}
        })

    index.upsert(vectors)
    print(f"Uploaded {len(vectors)} chunks to Pinecone.")


# Run uploader
if __name__ == "__main__":
    import asyncio
    asyncio.run(upload_chunks())
