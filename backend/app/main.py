# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTERS
from app.routes.chat import router as chat_router
from server.main import router as server_router

app = FastAPI(
    title="Suraj AI Chat Framework",
    version="1.0"
)

# -------------------------------------------------------
# CORS
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# ROUTES
# -------------------------------------------------------
app.include_router(chat_router)
app.include_router(server_router)

@app.get("/")
async def root():
    return {"status": "running"}
