"""Main FastAPI application with infrastructure initialization."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_database, init_session_factory
from app.core.storage import init_storage
from app.api import projects_router, chapters_router


# Global database engine
db_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize infrastructure on startup, cleanup on shutdown."""
    global db_engine

    # Startup
    print("Initializing infrastructure...")

    # Initialize database
    db_engine = init_database(settings)
    print(f"Database initialized at: {settings.database_url}")

    # Initialize session factory for dependency injection
    init_session_factory(db_engine)
    print("Session factory initialized")

    # Initialize storage
    init_storage(settings)
    print(f"Storage initialized at: {settings.storage_path}")

    # Make engine available to the app
    app.state.db_engine = db_engine

    yield

    # Shutdown
    print("Shutting down infrastructure...")
    if db_engine:
        db_engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Book Generator API",
    description="Professional book generator with PDF export",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Book Generator API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if db_engine else "disconnected",
        "storage": settings.storage_root.exists(),
    }


# Include API routers
app.include_router(projects_router)
app.include_router(chapters_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
