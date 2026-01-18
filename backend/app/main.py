"""
Hanyang: The Foundation - Main Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, lobby
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Hanyang: The Foundation",
    description="조선 초기 한양 건설 전략 보드게임 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(lobby.router, prefix="/api/v1/lobbies", tags=["Lobby"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Hanyang: The Foundation API",
        "version": "0.1.0",
        "docs": "/docs",
    }
