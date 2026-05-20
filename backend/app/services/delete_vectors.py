from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "suraj-chat-rag-index"

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY missing")

print("🔌 Connecting to Pinecone...")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

print("🧹 Deleting all vectors...")
index.delete(delete_all=True)

print("✅ All vectors deleted successfully.")
