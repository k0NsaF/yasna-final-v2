from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Lesson, Booking
from ..schemas import LessonCreate, LessonResponse, LessonPublicResponse
from ..security import get_current_master, get_current_family

router = APIRouter(tags=["Занятия"])

def lesson_with_places(lesson: Lesson, db: Session):
    booked_count = db.query(Booking).filter(Booking.lesson_id == lesson.id, Booking.status == "booked").count()
    return {
        "id": lesson.id, "title": lesson.title, "description": lesson.description,
        "starts_at": lesson.starts_at, "duration_minutes": lesson.duration_minutes,
        "capacity": lesson.capacity, "price": lesson.price, "is_active": lesson.is_active,
        "created_at": lesson.created_at, "booked_count": booked_count,
        "free_places": max(lesson.capacity - booked_count, 0),
    }

@router.post("/api/master/lessons", response_model=LessonResponse)
def create_lesson(data: LessonCreate, db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    lesson = Lesson(title=data.title, description=data.description, starts_at=data.starts_at, capacity=data.capacity)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

@router.get("/api/master/lessons", response_model=list[LessonPublicResponse])
def master_lessons(db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    lessons = db.query(Lesson).order_by(Lesson.starts_at).all()
    return [lesson_with_places(l, db) for l in lessons]

@router.get("/api/lessons", response_model=list[LessonPublicResponse])
def public_lessons(db: Session = Depends(get_db), family=Depends(get_current_family)):
    lessons = db.query(Lesson).filter(Lesson.is_active.is_(True)).order_by(Lesson.starts_at).all()
    return [lesson_with_places(l, db) for l in lessons]

@router.get("/api/lessons/{lesson_id}", response_model=LessonPublicResponse)
def get_lesson(lesson_id: int, db: Session = Depends(get_db), family=Depends(get_current_family)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    return lesson_with_places(lesson, db)