"""
WebSocket manager for real-time preview updates.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.services.markdown_processor import MarkdownProcessor, MarkdownConfig
from app.services.template_service import TemplateService
from app.services.chapter_service import ChapterService
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for live preview."""
    
    def __init__(self):
        """Initialize connection manager."""
        # Store active connections per project
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store last update time for debouncing
        self.last_update: Dict[int, datetime] = {}
        # Debounce delay in seconds
        self.debounce_delay = 1.0
        # Pending updates for debouncing
        self.pending_updates: Dict[int, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, project_id: int):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        logger.info(f"WebSocket connected for project {project_id}")
        
        # Send initial connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": "connection",
                "status": "connected",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def disconnect(self, websocket: WebSocket, project_id: int):
        """Remove a WebSocket connection."""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            # Clean up empty project sets
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
                
                # Cancel any pending updates for this project
                if project_id in self.pending_updates:
                    self.pending_updates[project_id].cancel()
                    del self.pending_updates[project_id]
        
        logger.info(f"WebSocket disconnected for project {project_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, project_id: int, message: dict):
        """Broadcast a message to all connections for a project."""
        if project_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[project_id].discard(conn)
    
    async def send_preview_update(
        self,
        project_id: int,
        chapter_id: Optional[int],
        content: str,
        db: Session,
        debounce: bool = True
    ):
        """Send preview update with optional debouncing."""
        if debounce:
            # Cancel any existing pending update
            if project_id in self.pending_updates:
                self.pending_updates[project_id].cancel()
            
            # Schedule new update
            self.pending_updates[project_id] = asyncio.create_task(
                self._delayed_preview_update(project_id, chapter_id, content, db)
            )
        else:
            # Send immediately
            await self._send_preview_now(project_id, chapter_id, content, db)
    
    async def _delayed_preview_update(
        self,
        project_id: int,
        chapter_id: Optional[int],
        content: str,
        db: Session
    ):
        """Send preview update after debounce delay."""
        try:
            await asyncio.sleep(self.debounce_delay)
            await self._send_preview_now(project_id, chapter_id, content, db)
        except asyncio.CancelledError:
            # Update was cancelled due to newer update
            pass
        finally:
            # Clean up pending updates
            if project_id in self.pending_updates:
                del self.pending_updates[project_id]
    
    async def _send_preview_now(
        self,
        project_id: int,
        chapter_id: Optional[int],
        content: str,
        db: Session
    ):
        """Send preview update immediately."""
        try:
            # Initialize processors
            markdown_processor = MarkdownProcessor()
            template_service = TemplateService()
            
            # Get project settings
            project_service = ProjectService(db)
            project = project_service.get_project(project_id)
            if not project:
                await self.broadcast(project_id, {
                    "type": "error",
                    "message": "Project not found",
                    "timestamp": datetime.utcnow().isoformat()
                })
                return
            
            # Configure markdown processing
            import json
            settings = {}
            if project.settings_json:
                settings = json.loads(project.settings_json)
            md_config = MarkdownConfig(
                enable_extra=True,
                enable_toc=settings.get("enable_toc", True),
                enable_footnotes=settings.get("enable_footnotes", True),
                enable_tables=True,
                enable_codehilite=True,
                enable_smarty=True,
                language=settings.get("language", "fr"),
                quotes_style="french" if settings.get("language", "fr") == "fr" else "english"
            )
            
            # Convert markdown to HTML
            html_content = markdown_processor.convert(content, md_config)
            
            # Get CSS for preview
            template_name = settings.get("template", "professional")
            css_content = template_service.generate_css(
                template_name=template_name,
                font_size=settings.get("font_size", 11),
                line_height=settings.get("line_height", 1.6)
            )
            
            # Prepare preview message
            message = {
                "type": "preview_update",
                "project_id": project_id,
                "chapter_id": chapter_id,
                "html": html_content,
                "css": css_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Broadcast to all connections
            await self.broadcast(project_id, message)
            
            # Update last update time
            self.last_update[project_id] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error generating preview for project {project_id}: {e}")
            await self.broadcast(project_id, {
                "type": "error",
                "message": f"Preview generation failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def send_chapter_update(
        self,
        project_id: int,
        chapter_id: int,
        action: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send chapter update notification."""
        message = {
            "type": "chapter_update",
            "action": action,  # created, updated, deleted, reordered
            "project_id": project_id,
            "chapter_id": chapter_id,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast(project_id, message)
    
    async def send_project_update(
        self,
        project_id: int,
        action: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send project update notification."""
        message = {
            "type": "project_update",
            "action": action,  # settings_changed, title_changed, etc.
            "project_id": project_id,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast(project_id, message)
    
    async def handle_client_message(
        self,
        websocket: WebSocket,
        project_id: int,
        message: dict,
        db: Session
    ):
        """Handle messages from client."""
        msg_type = message.get("type")
        
        if msg_type == "request_preview":
            # Client requests full preview
            chapter_id = message.get("chapter_id")
            
            if chapter_id:
                # Get specific chapter
                chapter_service = ChapterService(db)
                chapter = chapter_service.get_chapter(project_id, chapter_id)
                if chapter:
                    await self.send_preview_update(
                        project_id,
                        chapter_id,
                        chapter.content,
                        db,
                        debounce=False
                    )
            else:
                # Get all chapters
                chapter_service = ChapterService(db)
                chapters = chapter_service.list_chapters(project_id)
                
                # Combine all chapters
                combined_content = "\n\n".join([
                    f"# {ch.title}\n\n{ch.content}"
                    for ch in chapters
                ])
                
                await self.send_preview_update(
                    project_id,
                    None,
                    combined_content,
                    db,
                    debounce=False
                )
        
        elif msg_type == "content_update":
            # Client sends content update
            chapter_id = message.get("chapter_id")
            content = message.get("content", "")
            
            # Send preview with debouncing
            await self.send_preview_update(
                project_id,
                chapter_id,
                content,
                db,
                debounce=True
            )
        
        elif msg_type == "ping":
            # Respond to ping
            await self.send_personal_message(websocket, {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        else:
            logger.warning(f"Unknown message type: {msg_type}")


# Global connection manager instance
manager = ConnectionManager()