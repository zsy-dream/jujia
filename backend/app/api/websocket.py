"""
WebSocket endpoint for real-time health monitoring
Provides live updates for health status, activity, risk trends, and alerts
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime
import random

router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        await websocket.send_json(message)
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        """Broadcast a message to all connections for a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/health/{user_id}")
async def websocket_health_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time health monitoring
    
    Sends periodic updates for:
    - Health status and frailty score
    - Activity summary (steps, sleep, mobility)
    - Risk trends
    - Alerts and notifications
    """
    await manager.connect(websocket, user_id)
    
    try:
        # Send initial health status
        await manager.send_personal_message({
            "type": "health_status",
            "status": "normal",
            "frailty_score": 0.15,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Send initial activity summary
        await manager.send_personal_message({
            "type": "activity_update",
            "daily_steps": 5420,
            "sleep_hours": 7.5,
            "mobility_score": 0.85,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Send initial risk trends (last 7 days)
        trends = []
        for i in range(7):
            trends.append({
                "date": (datetime.now().timestamp() - (6 - i) * 86400),
                "risk_score": 0.1 + random.random() * 0.2
            })
        
        await manager.send_personal_message({
            "type": "risk_trend",
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Keep connection alive and send periodic updates
        while True:
            # Wait for 10 seconds between updates
            await asyncio.sleep(10)
            
            # Send updated health status
            frailty_score = 0.1 + random.random() * 0.3
            await manager.send_personal_message({
                "type": "health_status",
                "status": "normal" if frailty_score < 0.3 else "caution",
                "frailty_score": frailty_score,
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
            # Occasionally send activity updates
            if random.random() > 0.7:
                await manager.send_personal_message({
                    "type": "activity_update",
                    "daily_steps": 5000 + random.randint(0, 3000),
                    "sleep_hours": 6.5 + random.random() * 2,
                    "mobility_score": 0.7 + random.random() * 0.3,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            # Occasionally send alerts (low probability for demo)
            if random.random() > 0.95:
                severity_options = ["low", "medium", "high"]
                alert_types = ["activity", "health", "medication"]
                
                await manager.send_personal_message({
                    "type": "alert",
                    "alert_id": f"alert-{datetime.now().timestamp()}",
                    "alert_type": random.choice(alert_types),
                    "severity": random.choice(severity_options),
                    "message": "检测到活动模式异常，建议关注",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


async def send_health_update(user_id: str, health_data: dict):
    """
    Send health status update to all connected clients for a user
    Called by other services when health data changes
    """
    message = {
        "type": "health_status",
        "status": health_data.get("status", "normal"),
        "frailty_score": health_data.get("frailty_score", 0.0),
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_user(message, user_id)


async def send_activity_update(user_id: str, activity_data: dict):
    """Send activity summary update to connected clients"""
    message = {
        "type": "activity_update",
        "daily_steps": activity_data.get("daily_steps", 0),
        "sleep_hours": activity_data.get("sleep_hours", 0),
        "mobility_score": activity_data.get("mobility_score", 0),
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_user(message, user_id)


async def send_alert(user_id: str, alert_data: dict):
    """Send alert notification to connected clients"""
    message = {
        "type": "alert",
        "alert_id": alert_data.get("alert_id"),
        "alert_type": alert_data.get("alert_type"),
        "severity": alert_data.get("severity"),
        "message": alert_data.get("message"),
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_user(message, user_id)
