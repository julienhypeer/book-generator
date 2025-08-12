"""
Tests for WebSocket preview functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.project import Project
from app.models.chapter import Chapter
from app.services.project_service import ProjectService
from app.services.chapter_service import ChapterService
from app.websocket.preview_manager import ConnectionManager, manager


class TestWebSocketPreview:
    """Test suite for WebSocket preview functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client with WebSocket support."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_project(self, db_session: Session):
        """Create a sample project with chapters."""
        from app.validators.project import ProjectCreate
        from app.validators.chapter import ChapterCreate
        
        project_service = ProjectService(db_session)
        project_data = ProjectCreate(
            title="WebSocket Test Book",
            author="Test Author",
            settings={
                "language": "fr",
                "enable_toc": True,
                "template": "professional"
            }
        )
        project = project_service.create_project(project_data)
        
        chapter_service = ChapterService(db_session)
        chapter_data = ChapterCreate(
            title="Test Chapter",
            content="# Test\n\nThis is **bold** text.",
            position=1
        )
        chapter = chapter_service.create_chapter(project.id, chapter_data)
        
        return project, chapter
    
    def test_websocket_connection(self, client, sample_project):
        """Test WebSocket connection and initial message."""
        project, _ = sample_project
        
        with client.websocket_connect(f"/ws/preview/{project.id}") as websocket:
            # Should receive connection confirmation
            data = websocket.receive_json()
            
            assert data["type"] == "connection"
            assert data["status"] == "connected"
            assert data["project_id"] == project.id
    
    def test_websocket_preview_request(self, client, sample_project):
        """Test requesting preview through WebSocket."""
        project, chapter = sample_project
        
        with client.websocket_connect(f"/ws/preview/{project.id}") as websocket:
            # Skip connection message
            websocket.receive_json()
            
            # Request preview
            websocket.send_json({
                "type": "request_preview",
                "chapter_id": chapter.id
            })
            
            # Should receive preview update
            data = websocket.receive_json()
            
            assert data["type"] == "preview_update"
            assert data["project_id"] == project.id
            assert data["chapter_id"] == chapter.id
            assert "<h1>" in data["html"]
            assert "<strong>bold</strong>" in data["html"]
            assert "css" in data
    
    def test_websocket_content_update(self, client, sample_project):
        """Test sending content updates through WebSocket."""
        project, chapter = sample_project
        
        with client.websocket_connect(f"/ws/preview/{project.id}") as websocket:
            # Skip connection message
            websocket.receive_json()
            
            # Send content update
            websocket.send_json({
                "type": "content_update",
                "chapter_id": chapter.id,
                "content": "# Updated\n\n*Italic* text."
            })
            
            # Wait for debounced update
            import time
            time.sleep(1.5)
            
            # Should receive preview update
            data = websocket.receive_json()
            
            assert data["type"] == "preview_update"
            assert "<h1>" in data["html"]
            assert "<em>Italic</em>" in data["html"] or "<em>italic</em>" in data["html"].lower()
    
    def test_websocket_ping_pong(self, client, sample_project):
        """Test ping/pong keep-alive."""
        project, _ = sample_project
        
        with client.websocket_connect(f"/ws/preview/{project.id}") as websocket:
            # Skip connection message
            websocket.receive_json()
            
            # Send ping
            websocket.send_json({
                "type": "ping"
            })
            
            # Should receive pong
            data = websocket.receive_json()
            
            assert data["type"] == "pong"
            assert "timestamp" in data
    
    def test_websocket_invalid_project(self, client):
        """Test WebSocket connection with invalid project ID."""
        # Try to connect to non-existent project
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/preview/invalid-id") as websocket:
                pass
    
    def test_websocket_french_typography(self, client, sample_project):
        """Test French typography in preview."""
        project, chapter = sample_project
        
        with client.websocket_connect(f"/ws/preview/{project.id}") as websocket:
            # Skip connection message
            websocket.receive_json()
            
            # Send content with quotes
            websocket.send_json({
                "type": "content_update",
                "chapter_id": chapter.id,
                "content": '"Les guillemets" sont importants.'
            })
            
            # Wait for update
            import time
            time.sleep(1.5)
            
            # Should receive preview with French quotes
            data = websocket.receive_json()
            
            assert data["type"] == "preview_update"
            # Check for French guillemets
            assert "«" in data["html"] or "guillemets" in data["html"]


class TestConnectionManager:
    """Test suite for ConnectionManager."""
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket."""
        async def async_noop():
            return None
        
        mock = MagicMock()
        mock.send_json = MagicMock(return_value=async_noop())
        mock.accept = MagicMock(return_value=async_noop())
        return mock
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, mock_websocket):
        """Test connection and disconnection."""
        manager = ConnectionManager()
        project_id = "test-project"
        
        # Connect
        await manager.connect(mock_websocket, project_id)
        
        assert project_id in manager.active_connections
        assert mock_websocket in manager.active_connections[project_id]
        
        # Disconnect
        manager.disconnect(mock_websocket, project_id)
        
        assert project_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast(self, mock_websocket):
        """Test broadcasting to multiple connections."""
        manager = ConnectionManager()
        project_id = "test-project"
        
        # Connect multiple websockets
        async def async_noop():
            return None
            
        mock_ws1 = mock_websocket
        mock_ws2 = MagicMock()
        mock_ws2.send_json = MagicMock(return_value=async_noop())
        
        await manager.connect(mock_ws1, project_id)
        await manager.connect(mock_ws2, project_id)
        
        # Broadcast message
        message = {"type": "test", "data": "test"}
        await manager.broadcast(project_id, message)
        
        # Both should receive the message
        mock_ws1.send_json.assert_called_with(message)
        mock_ws2.send_json.assert_called_with(message)
    
    @pytest.mark.asyncio
    async def test_debouncing(self):
        """Test preview update debouncing."""
        manager = ConnectionManager()
        project_id = "test-project"
        
        # Mock database session
        mock_db = MagicMock()
        
        # Schedule multiple updates rapidly
        await manager.send_preview_update(project_id, "ch1", "content1", mock_db, debounce=True)
        await manager.send_preview_update(project_id, "ch1", "content2", mock_db, debounce=True)
        await manager.send_preview_update(project_id, "ch1", "content3", mock_db, debounce=True)
        
        # Only the last update should be pending
        assert project_id in manager.pending_updates
        
        # Wait for debounce
        await asyncio.sleep(1.5)
        
        # Pending updates should be cleared
        assert project_id not in manager.pending_updates