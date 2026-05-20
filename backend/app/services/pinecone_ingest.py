# backend/app/services/pinecone_ingest.py

import csv
import os
import asyncio
from pinecone import Pinecone, ServerlessSpec
from app.core.llm import get_embedding_model   

# ENV
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

# EXACT INDEX NAME FROM YOUR PINECONE DASHBOARD
INDEX_NAME = "suraj-chat-rag-index"

# CORRECT CSV PATH - from backend folder
CSV_PATH = "app/data/knowledgebase.csv"


async def embed(text: str):
    """Generate embedding asynchronously"""
    embedder = get_embedding_model()
    return await embedder.aembed(text)


def ingest_csv_into_pinecone(csv_path=CSV_PATH):
    if not PINECONE_API_KEY:
        raise ValueError("❌ PINECONE_API_KEY missing in .env")

    print("🔗 Connecting to Pinecone…")

    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it does not exist
    existing = [i["name"] for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print("📌 Creating Pinecone index:", INDEX_NAME)
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=PINECONE_ENV
            )
        )

    index = pc.Index(INDEX_NAME)

    print("📥 Reading CSV…")
    vectors = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            question = row["question"].strip()
            answer = row["answer"].strip()

            # async embedding call inside sync process
            embedding = asyncio.run(embed(question))

            vectors.append({
                "id": f"q_{i}",
                "values": embedding,
                "metadata": {
                    "question": question,
                    "answer": answer
                }
            })

    print(f"📤 Uploading {len(vectors)} vectors to Pinecone…")
    index.upsert(vectors)

    print("✅ DONE! Knowledgebase uploaded successfully.")


if __name__ == "__main__":
    ingest_csv_into_pinecone()
