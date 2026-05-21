# backend/app/agents/rag_agent.py

from app.core.rag import RAG
from app.core.llm import llm_model
from app.core.cache import SimpleCache
from server.logger import log
import re

_rag_instance = None
_cache = SimpleCache()


def normalize_query(text: str) -> str:
    """
    Normalize query for stable embeddings and caching.
    """
    if not text:
        return text

    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    text = re.sub(r'\s+', ' ', text)     # normalize spaces
    return text


class RAGAgent:

    def __init__(self):
        global _rag_instance
        if _rag_instance is None:
            _rag_instance = RAG()

        self.rag = _rag_instance

    async def run(self, session_id: str, message: str, memory=None, **kwargs):

        # ------------------------------------------------
        # 🔥 NORMALIZATION
        # ------------------------------------------------
        raw_query = message.strip()
        normalized_query = normalize_query(raw_query)

        cache_key = normalized_query

        # ------------------------------------------------
        # 1️⃣ CACHE CHECK
        # ------------------------------------------------
        cached = _cache.get(cache_key)
        if cached:
            log.info("[RAG] Cache hit")
            return cached

        # ------------------------------------------------
        # 2️⃣ VECTOR SEARCH
        # ------------------------------------------------
        try:
            matches = await self.rag.query(
                text=normalized_query,
                top_k=7   # ✅ optimized
            )
        except Exception:
            log.exception("❌ RAG query failed")
            return None

        if not matches:
            log.info("[RAG] No vector matches")
            return None

        # ------------------------------------------------
        # 3️⃣ SIMILARITY FILTER
        # ------------------------------------------------
        strong_matches = []
        weak_matches = []
        fallback_matches = []

        for m in matches:
            score = m.get("score", 0)
            log.info(f"[RAG] Match score: {score}")

            if score >= 0.60:
                strong_matches.append(m)
            elif score >= 0.50:
                weak_matches.append(m)
            elif score >= 0.35:
                fallback_matches.append(m)

        if strong_matches:
            selected_matches = strong_matches
        elif weak_matches:
            selected_matches = weak_matches
        elif fallback_matches:
            log.info("[RAG] Using fallback similarity matches")
            selected_matches = fallback_matches
        else:
            log.info("[RAG] All matches below similarity threshold")
            return None

        # ------------------------------------------------
        # 4️⃣ BUILD CONTEXT
        # ------------------------------------------------
        snippets = []

        for m in selected_matches:
            meta = m.get("metadata", {})

            text = (
                meta.get("answer")
                or meta.get("text")
                or meta.get("content")
                or ""
            )

            if text:
                snippets.append(text[:400])   # ✅ optimized (was 1500)

        if not snippets:
            log.info("[RAG] No metadata content")
            return None

        context_text = "\n\n".join(snippets)

        # ------------------------------------------------
        # 5️⃣ GROUNDED LLM GENERATION (IMPROVED PROMPT)
        # ------------------------------------------------
        prompt = f"""
You are an AI assistant for NY Medical Training.

STRICT RULES:
- Answer ONLY from the provided context
- DO NOT add any extra information
- DO NOT guess or assume anything
- If answer is not clearly in context, say: "I don't have that information"
- Keep answers short and precise
- Preserve bullet points and formatting exactly

Context:
{context_text}

Question:
{raw_query}

Answer:
"""

        try:
            reply = await llm_model().acomplete(prompt)
            reply = reply.strip()

            # 🔎 Debug output
            log.info(f"[RAG RAW OUTPUT REPR]: {repr(reply)}")

            # ------------------------------------------------
            # 6️⃣ SAFE CACHE
            # ------------------------------------------------
            if reply:
                lower_reply = reply.lower()
                if (
                    "don't have that information" not in lower_reply
                    and "do not have that information" not in lower_reply
                    and "couldn't find" not in lower_reply
                    and "not clearly present" not in lower_reply
                ):
                    _cache.set(cache_key, reply)

            return reply

        except Exception:
            log.exception("❌ RAG LLM generation failed")
            return None