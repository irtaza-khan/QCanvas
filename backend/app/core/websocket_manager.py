"""
QCanvas WebSocket Manager

This module provides WebSocket connection management for real-time communication
between the frontend and backend. It handles connection lifecycle, message routing,
and broadcasting to connected clients.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import json
import logging
from typing import Dict, Set, Any, Optional, Callable
from datetime import datetime
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class WebSocketMessage(BaseModel):
    """
    WebSocket message model for type-safe message handling.
    
    This model defines the structure of messages exchanged between
    the frontend and backend via WebSocket connections.
    """
    
    type: str = Field(..., description="Message type identifier")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Message payload")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Message timestamp")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WebSocketConnection:
    """
    Represents a single WebSocket connection with metadata.
    
    This class wraps a WebSocket connection and provides additional
    metadata and state management for the connection.
    """
    
    def __init__(self, websocket: WebSocket, connection_id: str):
        """
        Initialize a WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            connection_id: Unique identifier for this connection
        """
        self.websocket = websocket
        self.connection_id = connection_id
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.user_id: Optional[str] = None
        self.session_data: Dict[str, Any] = {}
        self.is_active = True
    
    async def send_message(self, message: WebSocketMessage) -> bool:
        """
        Send a message to this connection.
        
        Args:
            message: WebSocketMessage to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            if self.is_active:
                await self.websocket.send_text(message.json())
                self.last_activity = datetime.utcnow()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send message to connection {self.connection_id}: {str(e)}")
            self.is_active = False
            return False
    
    async def send_json(self, data: Dict[str, Any]) -> bool:
        """
        Send JSON data to this connection.
        
        Args:
            data: Dictionary data to send
            
        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        try:
            if self.is_active:
                await self.websocket.send_text(json.dumps(data))
                self.last_activity = datetime.utcnow()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send JSON to connection {self.connection_id}: {str(e)}")
            self.is_active = False
            return False
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information.
        
        Returns:
            Dict containing connection metadata
        """
        return {
            "connection_id": self.connection_id,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "user_id": self.user_id,
            "is_active": self.is_active,
            "session_data": self.session_data
        }


class WebSocketManager:
    """
    Manages WebSocket connections and message routing.
    
    This class provides centralized management of WebSocket connections,
    including connection lifecycle, message routing, and broadcasting
    capabilities for the QCanvas application.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Dict[str, WebSocketConnection] = {}
        self.connection_counter = 0
        self.message_handlers: Dict[str, Callable] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Register default message handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler("ping", self._handle_ping)
        self.register_handler("subscribe", self._handle_subscribe)
        self.register_handler("unsubscribe", self._handle_unsubscribe)
        self.register_handler("simulation_update", self._handle_simulation_update)
        self.register_handler("conversion_progress", self._handle_conversion_progress)
    
    async def startup(self):
        """Start the WebSocket manager."""
        logger.info("Starting WebSocket manager...")
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())
        
        logger.info("WebSocket manager started successfully")
    
    async def shutdown(self):
        """Shutdown the WebSocket manager."""
        logger.info("Shutting down WebSocket manager...")
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all active connections
        for connection in list(self.active_connections.values()):
            await self.disconnect(connection.websocket)
        
        logger.info("WebSocket manager shutdown complete")
    
    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            
        Returns:
            str: Connection ID for the new connection
        """
        await websocket.accept()
        
        # Generate unique connection ID
        self.connection_counter += 1
        connection_id = f"conn_{self.connection_counter}_{datetime.utcnow().timestamp()}"
        
        # Create connection object
        connection = WebSocketConnection(websocket, connection_id)
        self.active_connections[connection_id] = connection
        
        logger.info(f"New WebSocket connection established: {connection_id}")
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            type="connection_established",
            data={
                "connection_id": connection_id,
                "message": "Welcome to QCanvas WebSocket API"
            }
        )
        await connection.send_message(welcome_message)
        
        return connection_id
    
    async def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance to disconnect
        """
        # Find connection by websocket
        connection_id = None
        for cid, conn in self.active_connections.items():
            if conn.websocket == websocket:
                connection_id = cid
                break
        
        if connection_id:
            connection = self.active_connections[connection_id]
            connection.is_active = False
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def handle_message(self, websocket: WebSocket, message_text: str):
        """
        Handle incoming WebSocket message.
        
        Args:
            websocket: FastAPI WebSocket instance
            message_text: Raw message text from client
        """
        try:
            # Parse message
            message_data = json.loads(message_text)
            message = WebSocketMessage(**message_data)
            
            # Find connection
            connection = self._get_connection_by_websocket(websocket)
            if not connection:
                logger.warning("Received message from unknown connection")
                return
            
            # Update activity
            connection.update_activity()
            
            # Route message to appropriate handler
            await self._route_message(connection, message)
            
        except ValidationError as e:
            logger.error(f"Invalid message format: {str(e)}")
            await self._send_error(websocket, "Invalid message format", str(e))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {str(e)}")
            await self._send_error(websocket, "Invalid JSON", str(e))
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self._send_error(websocket, "Internal error", str(e))
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a message handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")
    
    async def broadcast(self, message: WebSocketMessage, exclude_connection_id: Optional[str] = None):
        """
        Broadcast a message to all active connections.
        
        Args:
            message: WebSocketMessage to broadcast
            exclude_connection_id: Optional connection ID to exclude from broadcast
        """
        for connection_id, connection in self.active_connections.items():
            if connection_id != exclude_connection_id and connection.is_active:
                await connection.send_message(message)
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """
        Send a message to all connections of a specific user.
        
        Args:
            user_id: User ID to send message to
            message: WebSocketMessage to send
        """
        for connection in self.active_connections.values():
            if connection.user_id == user_id and connection.is_active:
                await connection.send_message(message)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket connection statistics.
        
        Returns:
            Dict containing connection statistics
        """
        active_count = len([c for c in self.active_connections.values() if c.is_active])
        total_count = len(self.active_connections)
        
        return {
            "active_connections": active_count,
            "total_connections": total_count,
            "connection_counter": self.connection_counter
        }
    
    def _get_connection_by_websocket(self, websocket: WebSocket) -> Optional[WebSocketConnection]:
        """Get connection object by WebSocket instance."""
        for connection in self.active_connections.values():
            if connection.websocket == websocket:
                return connection
        return None
    
    async def _route_message(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Route message to appropriate handler."""
        handler = self.message_handlers.get(message.type)
        if handler:
            try:
                await handler(connection, message)
            except Exception as e:
                logger.error(f"Error in message handler for type '{message.type}': {str(e)}")
                await self._send_error(connection.websocket, "Handler error", str(e))
        else:
            logger.warning(f"No handler registered for message type: {message.type}")
            await self._send_error(connection.websocket, "Unknown message type", f"No handler for '{message.type}'")
    
    async def _send_error(self, websocket: WebSocket, error_type: str, message: str):
        """Send error message to client."""
        try:
            error_message = WebSocketMessage(
                type="error",
                data={
                    "error_type": error_type,
                    "message": message
                }
            )
            await websocket.send_text(error_message.json())
        except Exception as e:
            logger.error(f"Failed to send error message: {str(e)}")
    
    async def _cleanup_inactive_connections(self):
        """Periodically cleanup inactive connections."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                current_time = datetime.utcnow()
                inactive_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    # Check if connection has been inactive for more than 1 hour
                    if (current_time - connection.last_activity).total_seconds() > 3600:
                        inactive_connections.append(connection_id)
                
                # Close inactive connections
                for connection_id in inactive_connections:
                    connection = self.active_connections[connection_id]
                    await self.disconnect(connection.websocket)
                    logger.info(f"Closed inactive connection: {connection_id}")
                
                if inactive_connections:
                    logger.info(f"Cleaned up {len(inactive_connections)} inactive connections")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in connection cleanup: {str(e)}")
    
    # Default message handlers
    async def _handle_ping(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Handle ping messages."""
        pong_message = WebSocketMessage(
            type="pong",
            data={"timestamp": datetime.utcnow().isoformat()}
        )
        await connection.send_message(pong_message)
    
    async def _handle_subscribe(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Handle subscription requests."""
        subscription_type = message.data.get("type") if message.data else None
        if subscription_type:
            connection.session_data["subscriptions"] = connection.session_data.get("subscriptions", [])
            connection.session_data["subscriptions"].append(subscription_type)
            
            response = WebSocketMessage(
                type="subscription_confirmed",
                data={"type": subscription_type, "message": f"Subscribed to {subscription_type}"}
            )
            await connection.send_message(response)
    
    async def _handle_unsubscribe(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Handle unsubscription requests."""
        subscription_type = message.data.get("type") if message.data else None
        if subscription_type:
            subscriptions = connection.session_data.get("subscriptions", [])
            if subscription_type in subscriptions:
                subscriptions.remove(subscription_type)
                connection.session_data["subscriptions"] = subscriptions
                
                response = WebSocketMessage(
                    type="unsubscription_confirmed",
                    data={"type": subscription_type, "message": f"Unsubscribed from {subscription_type}"}
                )
                await connection.send_message(response)
    
    async def _handle_simulation_update(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Handle simulation update messages."""
        # Broadcast simulation updates to all connections subscribed to simulation updates
        for conn in self.active_connections.values():
            if (conn.is_active and 
                "simulation" in conn.session_data.get("subscriptions", []) and
                conn.connection_id != connection.connection_id):
                await conn.send_message(message)
    
    async def _handle_conversion_progress(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Handle conversion progress messages."""
        # Broadcast conversion progress to all connections subscribed to conversion updates
        for conn in self.active_connections.values():
            if (conn.is_active and 
                "conversion" in conn.session_data.get("subscriptions", []) and
                conn.connection_id != connection.connection_id):
                await conn.send_message(message)
