import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.api.endpoints import router as dispute_router

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connections, Langfuse, etc.
    logger.info(f"Starting Autonomous Decision Engine in {settings.ENVIRONMENT} mode.")
    yield
    # Shutdown: Clean up connections
    logger.info("Shutting down engine.")

app = FastAPI(
    title="Autonomous Financial Dispute Decision Engine",
    description="AI-powered backend for evaluating financial transaction disputes using advanced RAG and LangGraph.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(dispute_router, prefix="/api/v1")

# Serve static files for the Premium Dashboard
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception as e:
    logger.warning(f"Static directory mounting failed: {e}")

@app.get("/")
async def root():
    """Redirect home to the premium dashboard."""
    return RedirectResponse(url="/static/dashboard.html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
