"""API endpoints."""

from .projects import router as projects_router
from .chapters import router as chapters_router

__all__ = ["projects_router", "chapters_router"]
