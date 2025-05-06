from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from geoalchemy2 import Geometry
from typing import List

app = FastAPI()
origins = ["http://localhost:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DATABASE_URL = "postgresql://tododb_hjet_user:3EgV7WjpZyzPZXnCbquoHqOuRugHlreD@dpg-d0c8ht9r0fns73e5r1d0-a:5432/tododb_hjet"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    location = Column(Geometry('POINT'))

Base.metadata.create_all(engine)

class Task(BaseModel):
    id: int
    title: str
    completed: bool
    location: dict

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    result = [
        {
            "id": task.id,
            "title": task.title,
            "completed": task.completed,
            "location": {
                "lat": db.execute(f"SELECT ST_Y('{task.location}'::geometry)").scalar(),
                "lng": db.execute(f"SELECT ST_X('{task.location}'::geometry)").scalar()
            } if task.location else None
        }
        for task in tasks
    ]
    db.close()
    return result

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    db = SessionLocal()
    location_wkt = f"POINT({task.location['lng']} {task.location['lat']})" if task.location else None
    db_task = TaskDB(id=task.id, title=task.title, completed=task.completed, location=location_wkt)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    response = {
        "id": db_task.id,
        "title": db_task.title,
        "completed": db_task.completed,
        "location": task.location
    }
    db.close()
    return response