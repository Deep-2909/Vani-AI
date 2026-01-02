from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from fastapi import WebSocket
from app.ws import manager


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Backend is running"}

from app.models.database import engine
from app.models.grievance import Base

Base.metadata.create_all(bind=engine)

from app.api.vapi import router as vapi_router

app.include_router(vapi_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except:
        manager.disconnect(websocket)
