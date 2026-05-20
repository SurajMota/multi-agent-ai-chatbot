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
    Removes punctuation, extra spaces, and lowercases.
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
        # 🔥 NORMALIZATION (NEW - FIXES ? ISSUE)
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
        # 2️⃣ VECTOR SEARCH (using normalized query)
        # ------------------------------------------------
        try:
            matches = await self.rag.query(
                text=normalized_query,
                top_k=8
            )
        except Exception:
            log.exception("❌ RAG query failed")
            return None

        if not matches:
            log.info("[RAG] No vector matches")
            return None

        # ------------------------------------------------
        # 3️⃣ SIMILARITY FILTER (Slightly more tolerant)
        # ------------------------------------------------
        strong_matches = []
        weak_matches = []
        fallback_matches = []

        for m in matches:
            score = m.get("score", 0)
            log.info(f"[RAG] Match score: {score}")

            if score >= 0.65:          # slightly reduced from 0.70
                strong_matches.append(m)
            elif score >= 0.50:
                weak_matches.append(m)
            elif score >= 0.35:        # slightly reduced fallback
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
                snippets.append(text[:1500])

        if not snippets:
            log.info("[RAG] No metadata content")
            return None

        context_text = "\n\n".join(snippets)

        # ------------------------------------------------
        # 5️⃣ GROUNDED LLM GENERATION
        # ------------------------------------------------
        prompt = f"""
You are a helpful assistant for NY Medical Training.

Rules:
- Answer ONLY using the provided context.
- If the answer is not clearly present, say you don't have that information.
- PRESERVE the original formatting from the context.
- If the context contains bullet points or lists, return them exactly as-is.
- Do NOT rewrite structured lists into paragraphs.
- Do NOT invent information.

Context:
{context_text}

Question:
{normalized_query}
"""

        try:
            reply = await llm_model().acomplete(prompt)
            reply = reply.strip()
            
            # 🔎 DEBUG: check formatting EXACTLY as returned
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
