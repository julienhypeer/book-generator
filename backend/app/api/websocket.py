"""
WebSocket endpoints for real-time preview.
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.websocket.preview_manager import manager
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/preview/{project_id}")
async def websocket_preview(
    websocket: WebSocket,
    project_id: int,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db_session)
):
    """
    WebSocket endpoint for real-time preview updates.
    
    Protocol:
    - Client connects with project_id
    - Server sends connection confirmation
    - Client can send:
        - request_preview: Request full preview
        - content_update: Send content changes
        - ping: Keep-alive ping
    - Server sends:
        - preview_update: HTML preview update
        - chapter_update: Chapter CRUD notifications
        - project_update: Project settings changes
        - error: Error messages
        - pong: Response to ping
    """
    # Verify project exists
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    
    if not project:
        await websocket.close(code=1008, reason="Project not found")
        return
    
    # TODO: Add authentication check with token
    # For now, accept all connections
    
    # Connect the websocket
    await manager.connect(websocket, project_id)
    
    try:
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle the message
            await manager.handle_client_message(
                websocket,
                project_id,
                data,
                db
            )
            
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket, project_id)
        logger.info(f"Client disconnected from project {project_id}")
    
    except Exception as e:
        # Unexpected error
        logger.error(f"WebSocket error for project {project_id}: {e}")
        manager.disconnect(websocket, project_id)
        
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Global WebSocket endpoint for system notifications.
    
    Used for:
    - Export completion notifications
    - System alerts
    - Background task updates
    """
    # TODO: Implement authentication
    
    await websocket.accept()
    
    try:
        # Keep connection alive
        while True:
            # Wait for messages
            data = await websocket.receive_json()
            
            # Echo back for now (ping/pong)
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info("Notification websocket disconnected")
    
    except Exception as e:
        logger.error(f"Notification websocket error: {e}")