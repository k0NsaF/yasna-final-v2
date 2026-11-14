from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import get_current_family
from ..models import Booking, Child, Lesson
from ..schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/api/family", tags=["Запись"])

@router.post("/bookings", response_model=BookingResponse)
def book_lesson(payload: BookingCreate, db: Session = Depends(get_db), family=Depends(get_current_family)):
    lesson = db.query(Lesson).filter(Lesson.id == payload.lesson_id).first()
    if not lesson:
        raise Exception("Занятие не найдено")
    
    existing = db.query(Booking).filter(Booking.child_id == payload.child_id, Booking.lesson_id == payload.lesson_id).first()
    if existing:
        raise Exception("Ребенок уже записан")
    
    booked = db.query(Booking).filter(Booking.lesson_id == lesson.id, Booking.status == "booked").count()
    if booked >= lesson.capacity:
        raise Exception("В группе нет свободных мест")

    booking = Booking(child_id=payload.child_id, lesson_id=payload.lesson_id, status="booked")
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/bookings/{booking_id}", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), family=Depends(get_current_family)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        booking.status = "cancelled"
        db.commit()
    return booking