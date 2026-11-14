from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import get_current_master, get_current_family
from ..models import Payment
from ..schemas import PaymentCreate, PaymentResponse

router = APIRouter(tags=["Платежи"])

@router.get("/api/family/payments", response_model=list[PaymentResponse])
def family_payments(db: Session = Depends(get_db), family=Depends(get_current_family)):
    return db.query(Payment).filter(Payment.family_id == family.id).all()

@router.get("/api/master/payments", response_model=list[PaymentResponse])
def master_payments(db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    return db.query(Payment).all()