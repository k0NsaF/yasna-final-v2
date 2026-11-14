from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import get_current_family
from ..models import Receipt, Payment

router = APIRouter(tags=["Чеки"])

@router.get("/api/family/payments/{payment_id}/receipt")
def get_family_receipts(payment_id: int, db: Session = Depends(get_db), family=Depends(get_current_family)):
    return db.query(Receipt).filter(Receipt.payment_id == payment_id).all()