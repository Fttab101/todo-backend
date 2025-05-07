
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



# Configurar CORS
origins = ["http://localhost:5173", "https://todo-frontend-fm7m.onrender.com/"],
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=None,  # Asegura que no haya conflictos
    expose_headers=["*"],
    )
app.include_router(tasks.router)