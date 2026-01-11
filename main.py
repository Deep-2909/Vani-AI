import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.retell_ws import router as retell_router
from app.api.retell_webhook import router as webhook_router  # Retell webhook handler
from app.api.manager import router as manager_router
from app.api.api_bridge import router as bridge_router  # NEW: Complete API Bridge
from app.ws import manager
from app.db import engine
from app.models.grievance import Base

app = FastAPI(title="Delhi Grievance AI Backend - Complete")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(api_router)
app.include_router(retell_router)
app.include_router(webhook_router)  # Retell webhook handler
app.include_router(manager_router)
app.include_router(bridge_router)  # NEW: All frontend-backend bridge endpoints

@app.get("/")
def home():
    return {
        "message": "Delhi Grievance AI Backend - Fully Integrated",
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Multi-intent voice AI",
            "Real-time analytics",
            "Call logs management",
            "Knowledge base",
            "Database sync",
            "Calling queue",
            "Agent configuration"
        ]
    }

# Create database tables
Base.metadata.create_all(bind=engine)

# WebSocket for dashboard updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
