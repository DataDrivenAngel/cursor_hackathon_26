"""
Meetup Organizing Information Support System - Main Application Entry Point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.config import settings
from app.database.connection import init_db, get_db
from app.models.database_models import Event
from app.routers import events, venues, speakers, marketing, kanban, sponsors, admin, workflow
from app.auth.router import router as auth_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    os.makedirs("data", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    await init_db()
    yield
    # Shutdown (cleanup if needed)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# Include routers
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])  # Disabled for local development
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(kanban.router, prefix="/kanban", tags=["Kanban"])
app.include_router(venues.router, prefix="/venues", tags=["Venues"])
app.include_router(speakers.router, prefix="/speakers", tags=["Speakers"])
app.include_router(marketing.router, prefix="/marketing", tags=["Marketing"])
app.include_router(sponsors.router, prefix="/sponsors", tags=["Sponsors"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(workflow.router, prefix="", tags=["Workflow"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - redirects to dashboard or login."""
    return templates.TemplateResponse("dashboard.html", {"request": request, "events": []})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
