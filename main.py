import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.vapi import router as vapi_router
from app.ws import manager

from app.db import engine
from app.models.grievance import Base


app = FastAPI(title="Delhi Grievance AI Backend")

# 🌐 CORS (OK for dev/demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Routers
app.include_router(api_router)
app.include_router(vapi_router)

# 🏠 Health check
@app.get("/")
def home():
    return {"message": "Backend is running"}

# 🗄️ DB init (OK for demo, replace with migrations later)
Base.metadata.create_all(bind=engine)

# 🔌 WebSocket for dashboard updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print("WebSocket error:", e)
        await manager.disconnect(websocket)
