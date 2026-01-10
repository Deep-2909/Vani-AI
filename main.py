import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router as api_router
from app.api.vapi import router as vapi_router
from app.api.retell_ws import router as retell_router # Ensure this file exists
from app.ws import manager
from app.db import engine
from app.models.grievance import Base

from app.api.manager import router as manager_router

app = FastAPI(title="Delhi Grievance AI Backend")

# 🌐 Fix 1: Comprehensive CORS for HTTP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# 📦 Routers
app.include_router(api_router)
app.include_router(vapi_router)
app.include_router(retell_router) # This connects your /llm-websocket path
app.include_router(manager_router)

@app.get("/")
def home():
    return {"message": "Backend is running"}

Base.metadata.create_all(bind=engine)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)