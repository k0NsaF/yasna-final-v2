from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import get_current_master
from ..schemas import AttendanceUpdate, AttendanceResponse
from ..models import Attendance, Booking

router = APIRouter(prefix="/api/master", tags=["Посещаемость"])

@router.put("/bookings/{booking_id}/attendance", response_model=AttendanceResponse)
def update_attendance(booking_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    att = db.query(Attendance).filter(Attendance.booking_id == booking_id).first()
    if not att:
        att = Attendance(booking_id=booking_id, status=payload.status)
        db.add(att)
    else:
        att.status = payload.status
    db.commit()
    db.refresh(att)
    return att

@router.get("/attendance")
def get_attendance(db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    return db.query(Attendance).all()