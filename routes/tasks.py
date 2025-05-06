# backend/routes/tasks.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from geoalchemy2 import Geometry
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from geoalchemy2.functions import ST_X, ST_Y
from typing import List
from config.database import Base, get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/tasks", tags=["tasks"])

class Location(BaseModel):
    lat: float
    lng: float

class Task(BaseModel):
    title: str
    completed: bool = False
    location: Optional[Location] = None

class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    location = Column(Geometry('POINT'))

@router.get("/", response_model=List[Task])
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(
        TaskDB.title,
        TaskDB.completed,
        TaskDB.location,
        ST_Y(TaskDB.location).label("lat"),
        ST_X(TaskDB.location).label("lng")
    ).all()
    result = [
        {
            "title": task.title,
            "completed": task.completed,
            "location": (
                {
                    "lat": task.lat,
                    "lng": task.lng
                }
                if task.location
                else None
            )
        }
        for task in tasks
    ]
    return result

@router.post("/", response_model=Task)
async def create_task(task: Task, db: Session = Depends(get_db)):
    location_wkt = f"POINT({task.location.lng} {task.location.lat})" if task.location else None
    db_task = TaskDB(title=task.title, completed=task.completed, location=location_wkt)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    location_dict = None
    if db_task.location:
        query = select(ST_Y(db_task.location).label("lat"), ST_X(db_task.location).label("lng"))
        result = db.execute(query).first()
        location_dict = {"lat": result.lat, "lng": result.lng}
    return {
        "title": db_task.title,
        "completed": db_task.completed,
        "location": location_dict
    }