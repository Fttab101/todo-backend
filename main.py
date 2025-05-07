
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.sql import text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
from typing import List, Optional
from routes import tasks

app = FastAPI()

app.include_router(tasks.router)

# Configurar CORS
origins = ["http://localhost:3000", "https://your-frontend.onrender.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
