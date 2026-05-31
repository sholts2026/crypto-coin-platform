from __future__ import annotations
import sys
import os

# Project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from backend.api import (
    trends, tokens, decisions, social, brand, risk, contracts, launch, agents, reports, overview
)

app = FastAPI(
    title="Crypto Coin Launch Command Center",
    description="Multi-agent AI system for crypto token research, concept generation, and launch preparation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(overview.router)
app.include_router(trends.router)
app.include_router(tokens.router)
app.include_router(decisions.router)
app.include_router(social.router)
app.include_router(brand.router)
app.include_router(risk.router)
app.include_router(contracts.router)
app.include_router(launch.router)
app.include_router(agents.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "name": "Crypto Coin Launch Command Center",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    try:
        from telegram_bot.bot import start_bot_thread
        start_bot_thread()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Telegram bot startup skipped: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
