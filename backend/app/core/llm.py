# backend/app/core/llm.py

from dotenv import load_dotenv
load_dotenv()

import os
from openai import AsyncOpenAI
from functools import lru_cache
from server.logger import log

# -------------------------------------------------------
# ENV VARS
# -------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
EMBED_MODEL = "text-embedding-3-small"

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing in environment variables")


client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# -------------------------------------------------------
# COMPLETION MODEL
# -------------------------------------------------------
class LLMModel:
    async def acomplete(self, prompt: str) -> str:
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
            return response.choices[0].message.content

        except Exception as e:
            log.exception("LLM completion failed", exc_info=e)
            return "I'm sorry, I couldn't process that request."


# -------------------------------------------------------
# EMBEDDING MODEL
# -------------------------------------------------------
class EmbeddingModel:
    async def aembed(self, text: str):
        try:
            resp = await client.embeddings.create(
                model=EMBED_MODEL,
                input=text
            )
            return resp.data[0].embedding

        except Exception as e:
            log.exception("Embedding failed", exc_info=e)
            return []


# -------------------------------------------------------
# CACHED INSTANCES
# -------------------------------------------------------
@lru_cache()
def llm_model():
    return LLMModel()


@lru_cache()
def get_embedding_model():
    return EmbeddingModel()
