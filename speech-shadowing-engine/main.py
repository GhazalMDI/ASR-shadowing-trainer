from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from beanie import init_beanie
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import motor.motor_asyncio
import os
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",     
    "http://localhost:80",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/audio',StaticFiles(directory="audio"),name="audio")


@app.on_event("startup")
async def app_init():
    from models.accounts import User, RefreshToken, User_Audio, Listening_Logs
    from models.episodes import Episode

    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_IP"))
    db = client.speech_shadowing

    await init_beanie(
        database=db,
        document_models=[
            User,
            RefreshToken,
            User_Audio,
            Listening_Logs,
            Episode
        ]
    )
    

    from router import accounts, dashboard,episodes
    app.include_router(accounts.router)
    app.include_router(dashboard.router)
    app.include_router(episodes.router)
    
    
    
