from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Subscription
from ..schemas import SubscriptionCreate, SubscriptionResponse, SubscriptionBalance
from ..security import get_current_master, get_current_family

router = APIRouter(tags=["Абонементы"])

@router.post("/api/master/subscriptions", response_model=SubscriptionResponse)
def create_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    sub = Subscription(family_id=payload.family_id, title=payload.title, total_lessons=payload.total_lessons, price=payload.price)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/api/master/subscriptions", response_model=list[SubscriptionResponse])
def get_all_subscriptions(db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    return db.query(Subscription).all()

@router.get("/api/family/subscriptions/balance", response_model=SubscriptionBalance)
def get_family_subscription_balance(db: Session = Depends(get_db), family=Depends(get_current_family)):
    subs = db.query(Subscription).filter(Subscription.family_id == family.id, Subscription.is_active.is_(True)).all()
    total = sum(s.total_lessons for s in subs)
    used = sum(s.used_lessons for s in subs)
    return {"total_lessons": total, "used_lessons": used, "remaining_lessons": max(0, total - used), "money_balance": 0}