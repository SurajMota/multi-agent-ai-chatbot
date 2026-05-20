# backend/app/core/rag.py

from app.config import settings
from server.logger import log
from app.core.llm import get_embedding_model

# Try NEW SDK first, fallback to OLD
try:
    from pinecone import Pinecone
    NEW_PINECONE = True
except Exception:
    import pinecone
    NEW_PINECONE = False


class RAG:
    """
    SAFE Pinecone RAG wrapper
    ✔ Supports OLD + NEW Pinecone SDK
    ✔ Never crashes app
    ✔ Auto-disables if Pinecone fails
    """

    def __init__(
        self,
        index_name: str = "suraj-chat-rag-index",
        dimension: int = 1536,  # text-embedding-3-small
    ):
        self.index_name = index_name
        self.dimension = dimension
        self.index = None
        self.embedding_model = get_embedding_model()

        self._init_pinecone()

    # ---------------------------------------------------
    # SAFE INITIALIZATION
    # ---------------------------------------------------
    def _init_pinecone(self):
        if not settings.PINECONE_API_KEY:
            log.warning("⚠ Pinecone API key missing — RAG disabled")
            return

        try:
            # ----------------------------------
            # NEW SDK (pinecone >= 3.x)
            # ----------------------------------
            if NEW_PINECONE:
                log.info("🔹 Using NEW Pinecone SDK")

                pc = Pinecone(api_key=settings.PINECONE_API_KEY)

                existing = pc.list_indexes().names()

                if self.index_name not in existing:
                    pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric="cosine",
                        spec={
                            "serverless": {
                                "cloud": "aws",
                                "region": "us-east-1"
                            }
                        }
                    )

                self.index = pc.Index(self.index_name)

            # ----------------------------------
            # OLD SDK (pinecone-client)
            # ----------------------------------
            else:
                log.info("🔹 Using OLD Pinecone SDK")

                if not settings.PINECONE_ENV:
                    log.warning("⚠ Pinecone ENV missing — RAG disabled")
                    return

                pinecone.init(
                    api_key=settings.PINECONE_API_KEY,
                    environment=settings.PINECONE_ENV
                )

                if self.index_name not in pinecone.list_indexes():
                    pinecone.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric="cosine"
                    )

                self.index = pinecone.Index(self.index_name)

            log.info("✅ Pinecone RAG initialized successfully")

        except Exception:
            log.exception("❌ Pinecone init failed — RAG disabled")
            self.index = None

    # ---------------------------------------------------
    # EMBED TEXT
    # ---------------------------------------------------
    async def embed_text(self, text: str):
        return await self.embedding_model.aembed(text)

    # ---------------------------------------------------
    # QUERY VECTOR STORE
    # ---------------------------------------------------
    async def query(self, text: str, top_k: int = 4):
        if not self.index:
            return []

        vec = await self.embed_text(text)
        if not vec:
            return []

        res = self.index.query(
            vector=vec,
            top_k=top_k,
            include_metadata=True
        )

        return res.get("matches", [])
