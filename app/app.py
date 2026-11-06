
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.routers import auth

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudentHub API",
    description="API quản lý học tập StudentHub",
    version="1.0.0"
)

allowed_origins = json.loads(
    os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000","http://localhost:5173"]')
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)


@app.get("/", summary="Kiểm tra trạng thái Server")
def root():
    return {
        "message": "StudentHub API đang hoạt động"
    }
