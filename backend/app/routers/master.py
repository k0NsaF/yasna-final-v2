from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Family, Child, FamilyToken
from ..schemas import MasterLogin, MasterLoginResponse, FamilyCreate, FamilyResponse, ChildCreate, ChildResponse, FamilyLinkResponse, MessageResponse
from ..security import create_master_session, generate_family_token, get_current_master

router = APIRouter(prefix="/api/master", tags=["Мастер"])

@router.post("/login", response_model=MasterLoginResponse)
def master_login(data: MasterLogin):
    token = create_master_session(data.password)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def master_me(_: bool = Depends(get_current_master)):
    return {"authenticated": True, "role": "master"}

@router.post("/families", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(data: FamilyCreate, db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    family = Family(name=data.name, phone=data.phone)
    db.add(family)
    db.commit()
    db.refresh(family)
    return family

@router.get("/families")
def get_families(db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    families = db.query(Family).all()
    return families

@router.post("/families/{family_id}/children", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(family_id: int, data: ChildCreate, db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    family = db.query(Family).filter(Family.id == family_id).first()
    if family is None:
        raise HTTPException(status_code=404, detail="Семья не найдена")
    child = Child(family_id=family.id, first_name=data.first_name, last_name=data.last_name, birth_date=data.birth_date)
    db.add(child)
    db.commit()
    db.refresh(child)
    return child

@router.post("/families/{family_id}/link", response_model=FamilyLinkResponse)
def create_family_link(family_id: int, db: Session = Depends(get_db), _: bool = Depends(get_current_master)):
    family = db.query(Family).filter(Family.id == family_id).first()
    if family is None:
        raise HTTPException(status_code=404, detail="Семья не найдена")
    active_tokens = db.query(FamilyToken).filter(FamilyToken.family_id == family_id, FamilyToken.is_active == True).all()
    now = datetime.utcnow()
    for old_token in active_tokens:
        old_token.is_active = False
        old_token.revoked_at = now
    plain_token, token_hash = generate_family_token()
    new_token = FamilyToken(family_id=family_id, token_hash=token_hash, is_active=True)
    db.add(new_token)
    db.commit()
    return {"family_id": family_id, "access_token": plain_token, "token_type": "bearer", "message": "Сохраните токен"}