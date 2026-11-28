import logging
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("student-api")

app = FastAPI(
    title="Student Management API",
    description="A containerized FastAPI service for managing student records with structured logging and health checks.",
    version="1.0.0",
)


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    course: str = Field(..., min_length=1, max_length=120)
    semester: int = Field(..., ge=1, le=12)


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    course: Optional[str] = Field(None, min_length=1, max_length=120)
    semester: Optional[int] = Field(None, ge=1, le=12)


class Student(StudentCreate):
    id: int


students_db: List[dict] = [
    {"id": 1, "name": "Aarav Sharma", "course": "Backend Development", "semester": 5},
    {"id": 2, "name": "Diya Verma", "course": "Backend Development", "semester": 5},
    {"id": 3, "name": "Rohan Mehta", "course": "Cloud Computing", "semester": 6},
]
next_id = 4


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "method=%s path=%s status=500 duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise


@app.get("/")
def root():
    return {
        "application": "Student Management API",
        "framework": "FastAPI",
        "status": "running",
        "routes": {
            "health": "/health",
            "students": "/students",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/students", response_model=List[Student])
def list_students(course: Optional[str] = Query(default=None, description="Filter students by course name")):
    if course:
        return [s for s in students_db if s["course"].lower() == course.lower()]
    return students_db


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate):
    global next_id
    new_student = {
        "id": next_id,
        "name": payload.name,
        "course": payload.course,
        "semester": payload.semester,
    }
    students_db.append(new_student)
    next_id += 1
    return new_student


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, payload: StudentUpdate):
    for student in students_db:
        if student["id"] == student_id:
            if payload.name is not None:
                student["name"] = payload.name
            if payload.course is not None:
                student["course"] = payload.course
            if payload.semester is not None:
                student["semester"] = payload.semester
            return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for index, student in enumerate(students_db):
        if student["id"] == student_id:
            removed = students_db.pop(index)
            return {"deleted": True, "student": removed}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
