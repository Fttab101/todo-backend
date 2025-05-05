from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List

app = FastAPI()

# Configurar CORS para desarrollo
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar base de datos
DATABASE_URL="postgresql://hmedina:Kfz8j81$5@PPSQL100.dns-servicio.com:5432/10472368_mvg"

#DATABASE_URL = "postgresql://user:password@localhost:5432/tododb"  # Actualiza con tus credenciales
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Usar sqlalchemy.orm.declarative_base en lugar de sqlalchemy.ext.declarative
Base = declarative_base()

# Modelo de la base de datos
class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    completed = Column(Boolean, default=False)

# Crear la tabla en la base de datos
Base.metadata.create_all(engine)

# Modelo para la API
class Task(BaseModel):
    id: int
    title: str
    completed: bool

# Endpoint para obtener todas las tareas
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    db.close()
    return tasks

# Endpoint para añadir una nueva tarea
@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    db = SessionLocal()
    db_task = TaskDB(id=task.id, title=task.title, completed=task.completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task